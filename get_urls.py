import argparse
from itertools import compress
import os
from urllib import request
from urllib.error import URLError
import time

from dir_tools import load_temp_dir, group_by_dir, validate_dir
from parser import extract_urls
from pathname import check_name, get_path, get_type, strip_path
from progressbar import Progressbar
import write_files

progressbar = Progressbar()

# ------------------------------------------------------------------------------
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

    parser.add_argument('--wait', '-w', type=float, default=0.0,
                         help='Seconds to wait in between url requests. Defaults to 0.0')

    parser.add_argument('--silent', '-s', action='store_true',
                         help='Disable all printing to stdout')

    parser.add_argument('--log', '-l', type=argparse.FileType('a'),
                         help='Write / append to download log file')

    return parser.parse_args()


# ------------------------------------------------------------------------------
def get_response(file_url):
    response = False
    try:
        response = request.urlopen(file_url)
    except URLError:
        response = False
    finally:
        return response


def download(url, filepath=''):
    response = get_response(url)

    if response:
        accept_bytes = response.getheader('Accept-Ranges') == 'bytes'
        content_length = response.getheader('Content-Length')

        if accept_bytes and content_length and all((n.isdigit() for n in content_length)):
            total_bytes = int(response.getheader('Content-Length'))
            progressbar.reset(url=url, total_bytes=total_bytes)
            read_bytes = 0
            nbytes = 1024

            with open(filepath, 'wb') as f:
                while read_bytes < total_bytes:
                    if total_bytes - read_bytes < nbytes:
                        nbytes = total_bytes - read_bytes
                    f.write(response.read(nbytes))
                    progressbar.update(nbytes)
                    read_bytes += nbytes

        else:
            progressbar.no_byte_headers(url)
            with open(filepath, 'wb') as f:
                f.write(response.read())

            progressbar.line_separator()

        return True

    else:
        return False


def timestamp():
    """Timestamp using locale’s appropriate date, time representation

    Returns: tuple (str, str)
    """

    return (time.strftime('%x'), time.strftime('%X'))


def batch_download_to_temp(urlist, temp_dir, wait=0.1):
    """Downloads all valid URLs to tmp subdirectory and collects details on completed requests.

    Returns: lists
    """

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
                completed.append((temp_path, url, net_subdir, filename, timestamp()))
            else:
                failed.append(url)
            time.sleep(wait)
    return completed, failed


# ------------------------------------------------------------------------------
def save_to_subdirs(urlist, dirsort_type, overwrite, wait):
    temp_root, temp_dir = load_temp_dir()
    completed, failed = batch_download_to_temp(urlist, temp_dir, wait=wait)

    if not completed:
        print('Download failed for all input URLs')
        return [], failed

    if dirsort_type == 'type':
        log_details = write_files.to_filetype_subdirs(completed, temp_root, overwrite)
    elif dirsort_type == 'host':
        log_details = write_files.to_host_subdirs(completed, temp_root, overwrite)
    else:
        log_details = write_files.to_cwd(completed, temp_root, overwrite)


    return log_details, failed

# >>> move to parser ---> extract_urls_from_files?
def process_input_files(files):
    """Parses file containing text for possible URLs.

    Args:
        files: iterable containing filepaths

    Returns:
        list of possible URLs
    """

    links = []
    for fn in files:
        with open(fn, 'r') as f:
            lines = [line.strip() for line in f if line.strip() != '']

        found_links = extract_urls(lines)
        if found_links:
            links.extend(found_links)

    if links:
        if len(files) > 1:
            links = sorted(set(links), key=lambda url: url[::-1])
    else:
        print('No valid URLs located within input files')

    return links


def main():
    args = parse_arguments()

    if args.input:
        urlist = process_input_files([infile.name for infile in args.input])
    else:
        urlist = extract_urls(args.urls)

    if args.reject:
        reject_types = ['.' + ft if not ft.startswith('.') else ft for ft in args.reject]
        urlist = [url for url in urlist if all((not url.endswith(ft) for ft in reject_types))]

    if args.extract:
        for url in urlist:
            print(url)
        return

    if args.dirprefix != os.getcwd():
        os.chdir(args.dirprefix)

    if not args.silent:
        print()
        progressbar.line_separator()

    sort_options = (args.hostsort, args.namesort, args.typesort)

    if any(sort_options):
        dirsort_type = list(compress(('host', 'name', 'type'), sort_options))[0]
    else:
        dirsort_type = ''

    log_details, failed = save_to_subdirs(urlist, dirsort_type, args.overwrite, args.wait)

    if args.log and log_details:
        write_files.to_logfile(args.log.name, log_details)

    if not args.silent:
        if log_details:
            print()
            url_found = len(urlist)
            url_retrieved = len(log_details)
            url_failed = len(failed)
            print('Extracted URLs: {}\nDownloaded: {}\nFailed: {}\n'.format(url_found, url_retrieved, url_failed))

        if failed:
            print('Failed URLs listed below:')
            for url in failed:
                print(url)
            print()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
