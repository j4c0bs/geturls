import argparse
from itertools import compress
import os
import re
from string import punctuation
import tempfile
from urllib import request
from urllib.error import URLError
from prep_filename import get_name, get_path
# ------------------------------------------------------------------------------
# >>> if -i is relative and -d is outside of cwd, chdir ok here?
# msg = 'Directory path entered is not valid: {}'.format(user_dir)
# raise argparse.ArgumentTypeError(msg)

def validate_dir(user_dir):
    user_dir = os.path.abspath(user_dir)

    if not os.path.exists(user_dir):
        os.mkdir(user_dir)

    # os.chdir(user_dir)
    return user_dir


def parse_arguments():
    parser = argparse.ArgumentParser(prog='get_urls',
                                     description='downloads urls parsed from file')

    input_group = parser.add_mutually_exclusive_group(required=True)
    subdir_group = parser.add_mutually_exclusive_group()

    input_group.add_argument('--input', '-i', nargs='+', type=argparse.FileType('r'),
                         help="Input file(s) to parse for URLS")

    input_group.add_argument('--urls', '-u', nargs='+', type=str,
                         help="Input text URL(s) to download")

    parser.add_argument('--dirprefix', '-d', type=validate_dir, default=os.getcwd(),
                         help='Root / parent directory to store all files and subdirectories - defaults to cwd')

    subdir_group.add_argument('--hostsort', action='store_true',
                               help='Create subdirectories based on host site')
    subdir_group.add_argument('--namesort', action='store_true',
                               help='Create subdirectories based on filenames')
    subdir_group.add_argument('--typesort', action='store_true',
                               help='Create subdirectories based on filetypes')

    parser.add_argument('--extract', '-x', action='store_true',
                         help='Skip download and print URLs to stdout')

    parser.add_argument('--overwrite', action='store_true',
                         help='Overwrite existing files of same name')

    parser.add_argument('--reject', '-r', type=str, nargs='+',
                         help='Skip filetypes entered')

    return parser.parse_args()

# ------------------------------------------------------------------------------
def get_data(file_url):
    data = False
    try:
        data = request.urlopen(file_url)
    except URLError:
        data = False
        print('URLError', file_url)
    finally:
        return data

def download(file_url, filepath=''):
    data = get_data(file_url)

    if data:
        if not filepath:
            filepath = file_url.rsplit('/',1)[1]
        with open(filepath, 'wb') as f:
            f.write(data.read())
        return True
    else:
        return False

# ------------------------------------------------------------------------------
is_url = re.compile(r"(((http)s?://)?(w{3}\.)?([\w\-]+)(:\d)?\.([a-z]+)/((\.?(\w*[~!@#\$%^&*\(\)\-_\+\=,;`.]*)+(/|\.)?)+)[^\/])$", re.IGNORECASE)
has_scheme = re.compile(r"^(http)s?://.+")

def extract_urls(lines):
    links = []
    for line in lines:
        split_words = (word for word in line.split(' ') if not word.isalnum())
        for word in split_words:
            word = word.lstrip(punctuation)
            valid_url = is_url.match(word)
            if valid_url:
                links.append(valid_url.group())

    return links

# ------------------------------------------------------------------------------

def save_to_filetype_subdirs(urlist, overwrite):
    temp_root = tempfile.mkdtemp()
    temp_dir = os.mkdir(os.path.join(temp_root, 'get_urls_temp'))
    namelist = []

    completed = []
    failed = []

    for url in urlist:
        filepath, filename = get_path(url, root=temp_dir, overwrite=overwrite)
        status = download(url, filepath)
        if status:
            completed.append(url)
            namelist.append(filename)
        else:
            failed.append(url)

    if not completed:
        print('All downloads failed')
        return False

    fn_types = [get_type(fn, subdir=True)[1] for fn in namelist]
    type_subdirs = sorted(set(fn_types))

    for subdir in type_subdirs:
        if not os.path.exists(subdir):
            os.mkdir(subdir)

    for temp_path, filename, filetype in zip(completed, namelist, fn_types):
        filepath = os.path.join(filetype, filename)
        os.rename(temp_path, filepath)

    check_temp = os.listdir(temp_dir)
    if check_temp:
        print('check_temp:', check_temp)

    return completed, failed



def save_to_subdirs(urlist, dirsort_type, overwrite):
    if dirsort_type == 'type':
        completed, failed = save_to_filetype_subdirs(urlist, overwrite)

    return completed, failed


def display(urlist):
    print('input urlist:')
    for url in urlist:
        print(url)

def process_input_files(files):
    links = []
    for fn in files:
        with open(fn, 'r') as f:
            lines = [line.strip() for line in f if line.strip() != '']

        found_links = extract_urls(lines)
        if found_links:
            links.extend(found_links)

    if links:
        if len(files) > 1:
            links = sorted(set(links))
    else:
        print('No valid URLs located within input files')

    return links

def write_files_to_cwd(urlist, overwrite):
    if not overwrite:
        url_to_fn = [(url, url.rsplit('/',1)[1]) for url in urlist]
    else:
        url_to_fn = [(url, get_name(url.rsplit('/',1)[1])) for url in urlist]

    failed = []
    for (url, fn) in url_to_fn:
        if not download(url, fn):
            failed.append(url)
        else:
            print('completed:', url)

    if failed:
        print('-'*80)
        print('The following URLs were not downloaded:')
        for url in failed:
            print(url)

def main():
    args = parse_arguments()

    if args.input:
        urlist = process_input_files([infile.name for infile in args.input])
    else:
        urlist = extract_urls(args.urls)

    if args.dirprefix != os.getcwd():
        os.chdir(args.dirprefix)

    if args.reject:
        urlist = [url for url in urlist if all((not url.endswith(ft) for ft in args.reject))]

    sort_options = (args.hostsort, args.namesort, args.typesort)

    if any(sort_options):
        dirsort_type = list(compress(('host', 'name', 'type'), sort_options))[0]
        completed, failed = save_to_subdirs(urlist, dirsort_type, args.overwrite)
    else:
        write_files_to_cwd(urlist, args.overwrite)
        # if not args.overwrite:
        #     url_to_fn = [(url, url.rsplit('/',1)[1]) for url in urlist]
        # else:
        #     url_to_fn = [(url, get_name(url.rsplit('/',1)[1])) for url in urlist]

    # display(urlist)

    # failed = []
    # for (url, fn) in url_to_fn:
    #     completed = download(url, fn)
    #     if not completed:
    #         failed.append(url)
    #     else:
    #         print('completed:', url)
    #
    # if failed:
    #     print('-'*80)
    #     print('The following URLs were not downloaded:')
    #     for url in failed:
    #         print(url)
    #     print('-'*80)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # args = parse_arguments()
    print()
    main()
    # print(args)
    print()
