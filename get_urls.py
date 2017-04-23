import argparse
from itertools import compress
import os
import re
from string import punctuation
import tempfile
import time
from urllib import request
from urllib.error import URLError
from prep_filename import get_name, get_path, get_type
# ------------------------------------------------------------------------------

def validate_dir(user_dir):
    user_dir = os.path.abspath(user_dir)

    if not os.path.exists(user_dir):
        os.mkdir(user_dir)

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
scheme_pattern = re.compile(r"^((http)s?:)?(//).+")
def has_scheme(url):
    if scheme_pattern.match(url):
        return True
    else:
        return False

def get_data(file_url):
    data = False
    try:
        data = request.urlopen(file_url)
    except URLError:
        data = False
        print('URLError', file_url)
    finally:
        return data

def download(url, filepath=''):
    if not has_scheme(url):
        slash_url = '//' + url
        if has_scheme(slash_url):
            url = slash_url
        else:
            return False

    data = get_data(url)

    if data:
        if not filepath:
            filepath = url.rsplit('/',1)[1]
        with open(filepath, 'wb') as f:
            f.write(data.read())
        return True
    else:
        return False

# ------------------------------------------------------------------------------
# filename = urllib.parse.unquote(url.rsplit('/',1)[1])
# is_url = re.compile(r"(((http)s?://)?(w{3}\.)?([\w\-]+)(:\d)?\.([a-z]+)/((\.?(\w*[~!@#\$%^&*\(\)\-_\+\=,;`.]*)+(/|\.)?)+)[^\/])$", re.IGNORECASE)
is_url = re.compile(r"(((http)s?://)?(w{3}\.)?([\w\-]+)(:\d)?\.([a-z]+)/((\.?(.+[^\/])+(/|\.)?)+)[^\/])$", re.IGNORECASE)
punc = punctuation.replace('/','')

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
def load_temp_dir():
    temp_root = tempfile.mkdtemp()
    temp_subname = 'GETURLS_TMP_{}'.format(int(time.time()))
    temp_dir = os.path.join(temp_root, temp_subname)
    os.mkdir(temp_dir)

    return temp_root, temp_dir

def save_to_filetype_subdirs(urlist, overwrite):
    temp_root, temp_dir = load_temp_dir()
    namelist = []

    completed = []
    failed = []

    for url in urlist:
        filepath, filename = get_path(url, root=temp_dir, overwrite=overwrite)
        status = download(url, filepath)
        if status:
            print('Downloaded:', url)
            completed.append(filepath)
            namelist.append(filename)
        else:
            failed.append(url)

    if not completed:
        print('All downloads failed')
        return completed, failed

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


def make_host_subdirs(net_paths):
    subdir_check = [not os.path.exists(subdir) for subdir in net_paths]
    new_subdirs = list(compress(net_paths, subdir_check))
    for subdirtree in new_subdirs:
        os.makedirs(subdirtree, exist_ok=True)
    return new_subdirs


def save_to_host_subdirs(urlist, overwrite):

    temp_root, temp_dir = load_temp_dir()
    hostpath_split = [tuple(url.rsplit('/',1)) for url in urlist]
    netloc_paths = sorted(set(subdir[0] for subdir in hostpath_split))

    ix_loc = list(map(str, range(len(netloc_paths))))
    hostpath2ix = dict(zip(netloc_paths, ix_loc))

    net_paths = [path.split('//')[1] if '//' in path else path for path in netloc_paths]
    ix2subdir = dict(zip(ix_loc, net_paths))

    for dir_ix in ix_loc:
        temp_subdir = os.path.join(temp_dir, dir_ix)
        os.mkdir(temp_subdir)

    completed = []
    failed = []

    temp_ix_paths = {dir_ix: [] for dir_ix in ix_loc}
    for url, (hostpath, filename) in zip(urlist, hostpath_split):
        dir_ix = hostpath2ix[hostpath]
        temp_path = os.path.join(hostpath2ix[hostpath], filename)

        status = download(url, temp_path)
        if status:
            completed.append(url)
            temp_ix_paths[dir_ix].append(temp_path)
        else:
            failed.append(url)

    if not completed:
        print('All downloads failed')
        return completed, failed

    new_subdirs = make_host_subdirs(net_paths)
    for is_new, dir_ix in zip(new_subdirs, ix_loc):
        for fpath in temp_ix_paths[dir_ix]:
            final_subdir = ix2subdir[dir_ix]
            if is_new or overwrite:
                final_path = os.path.join(final_subdir, os.path.basename(fpath))
            else:
                final_path = get_name(os.path.basename(fpath), root=final_subdir)

            os.rename(fpath, final_path)

    return completed, failed


def save_to_subdirs(urlist, dirsort_type, overwrite):
    if dirsort_type == 'type':
        completed, failed = save_to_filetype_subdirs(urlist, overwrite)

    if failed:
        print('Failed:')
        for url in failed:
            print(url)

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
