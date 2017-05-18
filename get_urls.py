import argparse
from itertools import compress
import os

from dir_tools import validate_directory
import download
from parser import extract_urls, extract_urls_from_files
import write_files
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

    parser.add_argument('--dirprefix', '-d', type=validate_directory, default=os.getcwd(),
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

    parser.add_argument('--wait', '-w', type=float, default=0.01,
                         help='Seconds to wait in between url requests. Defaults to 0.01')

    parser.add_argument('--silent', '-s', action='store_true',
                         help='Disable all printing to stdout')

    parser.add_argument('--log', '-l', type=argparse.FileType('a'),
                         help='Write / append to download log file')

    return parser.parse_args()


# ------------------------------------------------------------------------------
def save_to_subdirs(completed, dirsort_type, overwrite):

    if dirsort_type == 'type':
        log_details = write_files.to_filetype_subdirs(completed, overwrite)
    elif dirsort_type == 'host':
        log_details = write_files.to_host_subdirs(completed, overwrite)
    else:
        log_details = write_files.to_cwd(completed, overwrite)

    return log_details


def main():
    args = parse_arguments()

    if args.input:
        urlist = extract_urls_from_files([infile.name for infile in args.input])
    else:
        urlist = extract_urls(args.urls)

    if args.reject:
        reject_types = ['.' + ft if not ft.startswith('.') else ft for ft in args.reject]
        urlist = [url for url in urlist if all((not url.endswith(ft) for ft in reject_types))]

    if args.extract:
        for url in urlist:
            print(url)
        return 0

    if not args.silent:
        print()

    if args.dirprefix != os.getcwd():
        os.chdir(args.dirprefix)

    sort_options = (args.hostsort, args.namesort, args.typesort)

    if any(sort_options):
        dirsort_type = list(compress(('host', 'name', 'type'), sort_options))[0]
    else:
        dirsort_type = ''

    completed, failed, tmp_dir = download.to_tmp(urlist, args.wait, args.silent)

    if completed:
        log_details = save_to_subdirs(completed, dirsort_type, args.overwrite)
    else:
        log_details = False

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

    tmp_dir.cleanup()

    return 0


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
