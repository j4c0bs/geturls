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
is_url = re.compile(r'^(?:[a-z0-9\.\-\+]*)'
    r'://(?:\S+(?::\S*)?@)'
    r'?(?:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d))'
    r'{3}|\[[0-9a-f:\.]+\]|'
    r'([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?(?:\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))'
    r'*\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\.?|localhost))(?::\d{2,5})?(?:[/?#][^\s]*)?\Z',
    re.IGNORECASE|re.UNICODE)


def extract_urls_from_file(fn):
    links = []
    with open(fn, 'r') as f:
        lines = [line.strip() for line in f if line.strip() != '']

    for line in lines:
        split_words = (word for word in line.split(' ') if not word.isalnum())
        for word in split_words:
            cleaned = word.strip(punctuation)
            if is_url.match(cleaned):
                links.append(cleaned)

    return links

# ------------------------------------------------------------------------------
def make_dir_map(urlist, dirsort_type):
    # url_to_fn = {}
    pass


def display(urlist):
    print()
    for url in urlist:
        print(url)

def get_all_urls(files):
    links = []
    for fn in files:
        found_links = extract_urls_from_file(fn)
        if found_links:
            links.extend(found_links)

    if links:
        links = sorted(set(links), key=lambda url: url.count('/'))
    else:
        print('No valid Urls located within:\n')

    return links


def main():
    args = parse_arguments()
    urlist = get_all_urls((infile.name for infile in args.input))

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
        print('The following urls were not downloaded:')
        for url in failed:
            print(url)
        print('-'*80)

# ------------------------------------------------------------------------------
# In [75]: os.system('which wget')
# /usr/local/bin/wget
# Out[75]: 0
# >>> not found -> d == 256
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # args = parse_arguments()
    print()
    main()
    # print(args)
    print()


    # def make_file(fn):
    #     with open(fn, 'w') as txt:
    #         txt.write('Test File')
    #     return
    #
    # def generate_test_files(n, nsubdir):
    #     for ns in range(nsubdir):
    #         dir_name = 'test_folder_{}'.format(str(ns).rjust(2,'0'))
    #         if not os.path.exists(dir_name):
    #             os.mkdir(dir_name)
    #
    #         for x in range(n):
    #             txt_fn = 'TXT_{}.txt'.format(x)
    #             fn = os.path.join(dir_name, txt_fn)
    #             make_file(fn)
    #     return
