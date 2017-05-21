import os
import time
from urllib import request
from urllib.error import URLError

from dir_tools import load_temp_dir, group_by_dir, confirm_directory
from progressbar import Progressbar
# ------------------------------------------------------------------------------
def get_response(url):
    response = False
    try:
        response = request.urlopen(url)
    except URLError:
        response = False
    finally:
        return response


def silent_download(url, filepath, *ignore):
    response = get_response(url)
    if response:
        with open(filepath, 'wb') as f:
            f.write(response.read())
        return True
    else:
        return False


def verbose_download(url, filepath, progressbar):
    response = get_response(url)

    if response:
        accept_bytes = response.getheader('Accept-Ranges') == 'bytes'
        content_length = response.getheader('Content-Length')

        if accept_bytes and content_length and all((n.isdigit() for n in content_length)):
            total_bytes = int(content_length)
            progressbar.reset(url=url, total_bytes=total_bytes)
            read_bytes = 0
            nbytes = 1024
            loop_count = 1
            checkpoint = 32

            with open(filepath, 'wb') as f:
                while read_bytes < total_bytes:

                    if loop_count % checkpoint == 0:
                        chunk_factor = progressbar.download_rate / nbytes
                        if chunk_factor < 0.33:
                            nbytes //= 2
                        elif chunk_factor > 2:
                            nbytes *= 2
                        elif chunk_factor == 0:
                            progressbar.timeout()
                            break

                    if total_bytes - read_bytes < nbytes:
                        nbytes = total_bytes - read_bytes

                    f.write(response.read(nbytes))
                    progressbar.update(nbytes)
                    read_bytes += nbytes
                    loop_count += 1

            if os.path.getsize(filepath) != total_bytes:
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


def to_tmp(urlist, wait, quiet, silent):
    """Downloads all valid URLs to tmp subdirectory and collects details on completed requests.

    Args:
        - urlist: list of (url, filename)
        - wait: float - time in seconds to delay requests
        - quiet: bool - enables optional progressbar display
        - silent: bool - disables progressbar / any printing to stdout

    Returns:
        - completed
        - failed
        - tmp_dir
    """

    tmp_dir = load_temp_dir()

    completed = []
    failed = []
    dir_groups = group_by_dir(urlist)

    if silent:
        download = silent_download
        progressbar = None
    else:
        download = verbose_download
        progressbar = Progressbar(quiet=quiet, nfiles=len(urlist))

    for net_subdir, url_name_list in dir_groups.items():
        temp_subdir = os.path.join(tmp_dir.name, str(hash(net_subdir)))
        confirm_directory(temp_subdir)

        for (url, filename) in url_name_list:
            temp_path = os.path.join(temp_subdir, filename)
            status = download(url, temp_path, progressbar)

            if status:
                completed.append((temp_path, url, net_subdir, filename, timestamp()))
            else:
                failed.append(url)
            time.sleep(wait)

    if quiet and progressbar:
        progressbar.cleanup()

    return completed, failed, tmp_dir
