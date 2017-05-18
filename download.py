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
    end = 0

    if response:
        accept_bytes = response.getheader('Accept-Ranges') == 'bytes'
        content_length = response.getheader('Content-Length')

        if accept_bytes and content_length and all((n.isdigit() for n in content_length)):
            total_bytes = int(response.getheader('Content-Length'))
            progressbar.reset(url=url, total_bytes=total_bytes)
            read_bytes = 0
            nbytes = 1024
            loop_count = 1
            checkpoint = 32

            start = time.time()

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
                return False, (0,0)

            end = time.time() - start

        else:
            progressbar.no_byte_headers(url)
            with open(filepath, 'wb') as f:
                f.write(response.read())

            progressbar.line_separator()

        return True, (end, loop_count)

    else:
        return False, (0,0)


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
    secs = 0
    loops = 0
    tot_loops = []
    progressbar = Progressbar(silent)
    tmp_dir = load_temp_dir()

    completed = []
    failed = []
    dir_groups = group_by_dir(urlist)

    for net_subdir, url_name_list in dir_groups.items():
        temp_subdir = os.path.join(tmp_dir.name, str(hash(net_subdir)))
        confirm_directory(temp_subdir)

        for (url, filename) in url_name_list:
            temp_path = os.path.join(temp_subdir, filename)
            status, (end, loop_count) = download(url, temp_path, progressbar)
            secs += end
            loops += loop_count
            tot_loops.append(loop_count)

            if status:
                completed.append((temp_path, url, net_subdir, filename, timestamp()))
            else:
                failed.append(url)
            time.sleep(wait)

    print('\nLoops per second: {:.2f}'.format(loops/secs))
    print('Average time per download - dynamic chunk: {:.4f} sec'.format(secs / len(completed)))
    print('tot_loops:', tot_loops)

    return completed, failed, tmp_dir
