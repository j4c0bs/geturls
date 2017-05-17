import os
import time
from urllib import request
from urllib.error import URLError

from dir_tools import load_temp_dir, group_by_dir, confirm_directory
from progressbar import Progressbar
# ------------------------------------------------------------------------------
def get_response(file_url):
    response = False
    try:
        response = request.urlopen(file_url)
    except URLError:
        response = False
    finally:
        return response


def download(url, filepath, progressbar):
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

            if os.path.getsize(filepath) != total_bytes:
                print('total_bytes not equal:', filepath)
                return False

        else:
            progressbar.no_byte_headers(url)
            with open(filepath, 'wb') as f:
                f.write(response.read())

            progressbar.line_separator()

        return True

    else:
        return False


# ------------------------------------------------------------------------------
def timestamp():
    """Timestamp using locale’s appropriate date, time representation

    Returns: tuple (str, str)
    """

    return (time.strftime('%x'), time.strftime('%X'))


def to_tmp(urlist, wait, silent):
    """Downloads all valid URLs to tmp subdirectory and collects details on completed requests.

    Returns: lists
    """

    progressbar = Progressbar(silent)
    temp_root, temp_dir = load_temp_dir()

    completed = []
    failed = []
    dir_groups = group_by_dir(urlist)

    for net_subdir, url_name_list in dir_groups.items():
        temp_subdir = os.path.join(temp_dir, str(hash(net_subdir)))
        # os.mkdir(temp_subdir)
        confirm_directory(temp_subdir)

        for (url, filename) in url_name_list:
            temp_path = os.path.join(temp_subdir, filename)
            status = download(url, temp_path, progressbar)
            if status:
                completed.append((temp_path, url, net_subdir, filename, timestamp()))
            else:
                failed.append(url)
            time.sleep(wait)

    return completed, failed, temp_root
