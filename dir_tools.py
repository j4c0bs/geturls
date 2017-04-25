import os
import tempfile
import time
from urllib.parse import unquote as url_unquote
# ------------------------------------------------------------------------------
def confirm_dir(*subdirs):
    for subdir in subdirs:
        if not os.path.exists(subdir):
            os.mkdir(subdir)


def load_temp_dir():
    temp_root = tempfile.mkdtemp()
    temp_subname = 'GETURLS_TMP_{}'.format(int(time.time()))
    temp_dir = os.path.join(temp_root, temp_subname)
    os.mkdir(temp_dir)
    return temp_root, temp_dir


def group_by_dir(urlist):
    dir_groups = {}
    for url in urlist:
        net_subdir, filename = url_unquote(url).rsplit('/',1)
        if net_subdir in dir_groups:
            dir_groups[net_subdir].append((url, filename))
        else:
            dir_groups[net_subdir] = [(url, filename)]
    return dir_groups
