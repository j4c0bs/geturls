import os
import tempfile
import time
from urllib.parse import unquote as url_unquote
# ------------------------------------------------------------------------------
def confirm_directory(subdir):
    if os.path.exists(subdir):
        if not os.path.isdir(subdir):
            return False
    else:
        os.mkdir(subdir)
    return True


# def confirm_directory(subdir):
#     if not os.path.exists(subdir):
#         os.mkdir(subdir)


def validate_directory(user_dir):
    user_dir = os.path.abspath(user_dir)
    status = confirm_directory(user_dir)
    if status:
        return user_dir
    else:
        return os.curdir

# def validate_directory(user_dir):
#     user_dir = os.path.abspath(user_dir)
#     confirm_directory(user_dir)
#     return user_dir
#

def load_temp_dir():
    """Makes temporary directory with unique prefix.

    Returns:
        - tmp_dir: tempfile.TemporaryDirectory instance
    """

    temp_subname = 'GETURLS_TMP_{}'.format(int(time.time()))
    tmp_dir = tempfile.TemporaryDirectory(prefix=temp_subname)
    return tmp_dir


def group_by_dir(urlist):
    """Sorts urls into groups based on shared url directory paths.

    Returns:
        - dir_groups: dict
    """

    dir_groups = {}
    for url in urlist:
        net_subdir, filename = url_unquote(url).rsplit('/',1)
        if net_subdir in dir_groups:
            dir_groups[net_subdir].append((url, filename))
        else:
            dir_groups[net_subdir] = [(url, filename)]
    return dir_groups
