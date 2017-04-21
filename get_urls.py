import argparse
from itertools import compress
import os
import re
from string import punctuation
from urllib import request
from urllib.error import URLError
# ------------------------------------------------------------------------------
# >>> if -i is relative and -d is outside of cwd, chdir ok here?
# msg = 'Directory path entered is not valid: {}'.format(user_dir)
# raise argparse.ArgumentTypeError(msg)

def validate_dir(user_dir):
    user_dir = os.path.abspath(user_dir)

    if not os.path.exists(user_dir):
        os.mkdir(user_dir)

    os.chdir(user_dir)
    return user_dir


def parse_arguments():
    parser = argparse.ArgumentParser(prog='get_urls',
                                     description='downloads urls parsed from file')

    subdir_group = parser.add_mutually_exclusive_group()

    parser.add_argument('--input', '-i', nargs='+', type=argparse.FileType('r'),
                         help="Input file(s)", required=True)

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
    finally:
        return data

def download(file_url, fn):
    data = get_data(file_url)
    if data:
        with open(fn, 'wb') as f:
            f.write(data.read())
        return True
    else:
        return False

# ------------------------------------------------------------------------------
is_url = re.compile(r"(((http)s?://)?(w{3}\.)?([\w\-]+)(:\d)?\.([a-z]+)/((\.?(\w*[~!@#\$%^&*\(\)\-_\+\=,;`.]*)+(/|\.)?)+)[^\/])$")
has_scheme = re.compile(r"^(http)s?://.+")

def extract_urls(lines):
    links = []
    for line in lines:
        split_words = (word.lower() for word in line.split(' ') if not word.isalnum())
        for word in split_words:
            word = word.lstrip(punctuation)
            valid_url = is_url.match(word)
            if valid_url:
                links.append(valid_url.group())

    return links

# ------------------------------------------------------------------------------
def make_dir_map(urlist, dirsort_type):
    # url_to_fn = {}
    pass


def display(urlist):
    print()
    for url in urlist:
        print(url)

def process_input_files(files):
    links = []
    for fn in files:
        with open(fn, 'r') as f:
            lines = (line.strip() for line in f if line.strip() != '')

        found_links = extract_urls(lines)
        if found_links:
            links.extend(found_links)

    if links:
        if len(files) > 1:
            links = sorted(set(links))
    else:
        print('No valid URLs located within input files')

    return links


def main():
    args = parse_arguments()
    urlist = process_input_files((infile.name for infile in args.input))

    if args.reject:
        urlist = [url for url in urlist if all((not url.endswith(ft) for ft in args.reject))]

    sort_options = (args.hostsort, args.namesort, args.typesort)

    if any(sort_options):
        dirsort_type = list(compress(('host', 'name', 'type'), sort_options))[0]
        url_to_fn = make_dir_map(urlist, dirsort_type)
    else:
        url_to_fn = [(url, url.rsplit('/',1)[1]) for url in urlist]

    display(urlist)

    failed = []
    for (url, fn) in url_to_fn:
        completed = download(url, fn)
        if not completed:
            failed.append(url)

    if failed:
        print('-'*80)
        print('The following URLs were not downloaded:')
        for url in failed:
            print(url)
        print('-'*80)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # args = parse_arguments()
    print()
    main()
    # print(args)
    print()
