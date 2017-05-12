import argparse
from itertools import compress
import os
from urllib import request
from urllib.error import URLError
from dir_tools import confirm_dirs, load_temp_dir, group_by_dir
from parser import extract_urls
from pathname import check_name, get_path, get_type, strip_path
import write_files
# ------------------------------------------------------------------------------

def validate_dir(user_dir):
    user_dir = os.path.abspath(user_dir)

    if not os.path.exists(user_dir):
        os.mkdir(user_dir)

    return user_dir


def parse_arguments():
    parser = argparse.ArgumentParser(prog='get_urls',
                                     description='downloads urls parsed from file(s)')

    input_group = parser.add_mutually_exclusive_group(required=True)
    subdir_group = parser.add_mutually_exclusive_group()

    input_group.add_argument('--input', '-i', nargs='+', type=argparse.FileType('r'),
                              help="Input file(s) to parse for URLs")

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
        data = None
        print('URLError', file_url)
    finally:
        return data


def download(url, filepath=''):
    data = get_data(url)

    if data:
        if not filepath:
            filepath = strip_path(url)
        with open(filepath, 'wb') as f:
            f.write(data.read())
        return True
    else:
        return False


def batch_download_to_temp(urlist, temp_dir):
    completed = []
    failed = []
    dir_groups = group_by_dir(urlist)
    for net_subdir, url_name_list in dir_groups.items():
        temp_subdir = os.path.join(temp_dir, str(hash(net_subdir)))
        os.mkdir(temp_subdir)
        for (url, filename) in url_name_list:
            temp_path = os.path.join(temp_subdir, filename)
            status = download(url, filepath=temp_path)
            if status:
                completed.append((temp_path, net_subdir, filename))
            else:
                failed.append(url)
    return completed, failed

# ------------------------------------------------------------------------------
def save_to_subdirs(urlist, dirsort_type, overwrite):
    temp_root, temp_dir = load_temp_dir()
    completed, failed = batch_download_to_temp(urlist, temp_dir)

    # print('completed dl to /tmp')
    # for tmpath in completed:
    #     print(tmpath)

    if not completed:
        print('No URLs downloaded')
        # >>> TODO: what to return / exit?
        return False

    if dirsort_type == 'type':
        write_files.to_filetype_subdirs(completed, temp_root, overwrite)
    elif dirsort_type == 'host':
        write_files.to_host_subdirs(completed, temp_root, overwrite)
    else:
        write_files.to_cwd(completed, temp_root, overwrite)


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
            links = sorted(set(links), key = lambda url: url[::-1])
    else:
        print('No valid URLs located within input files')

    return links


def main():
    args = parse_arguments()

    if args.input:
        urlist = process_input_files([infile.name for infile in args.input])
    else:
        urlist = extract_urls(args.urls)

    if args.dirprefix != os.getcwd():
        os.chdir(args.dirprefix)

    if args.reject:
        reject_types = ['.' + ft if not ft.startswith('.') else ft for ft in args.reject]
        urlist = [url for url in urlist if all((not url.endswith(ft) for ft in reject_types))]

    if args.extract:
        # print(', '.join(urlist))
        for url in urlist:
            print(url)
        return

    sort_options = (args.hostsort, args.namesort, args.typesort)

    if any(sort_options):
        dirsort_type = list(compress(('host', 'name', 'type'), sort_options))[0]
    else:
        dirsort_type = ''

    completed, failed = save_to_subdirs(urlist, dirsort_type, args.overwrite)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print()
    main()
    print()
