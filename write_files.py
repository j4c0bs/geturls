from itertools import groupby
import os

from dir_tools import confirm_dirs
from pathname import get_type, get_path, split_name
# ------------------------------------------------------------------------------
def check_for_duplicates(all_names):
    duplicates = []
    all_names.sort(key=get_type)
    for filetype, names in groupby(all_names, get_type):
        namelist = list(names)
        nameset = set(namelist)
        if len(namelist) != len(nameset):
            duplicates.extend([name for name in nameset if namelist.count(name) > 1])

    return set(duplicates)


def to_cwd(completed, temp_root, overwrite):
    all_paths, all_netdirs, all_names = list(zip(*completed))

    namecache = set()
    for filepath, filename in zip(all_paths, all_names):
        discrete_name = filename not in namecache
        real_path, real_name = get_path(filename, overwrite=(overwrite and discrete_name))
        os.rename(filepath, real_path)
        namecache.add(filename)

# ------------------------------------------------------------------------------
def to_filetype_subdirs(completed, temp_root, overwrite):
    all_paths, all_netdirs, all_names = list(zip(*completed))
    fn_types = [get_type(fn, subdir=True)[1] for fn in all_names]
    type_subdirs = sorted(set(fn_types))
    confirm_dirs(*type_subdirs)

    namecache = set()
    for temp_path, filename, filetype in zip(all_paths, all_names, fn_types):
        discrete_name = filename not in namecache
        filepath = get_path(filename, root=filetype, overwrite=(overwrite and discrete_name))
        os.rename(temp_path, filepath)
        namecache.add(filename)

# ------------------------------------------------------------------------------
def to_host_subdirs(completed, temp_root, overwrite):
    all_paths, all_netdirs, all_names = list(zip(*completed))
    all_netdirs = [path.split('//')[1] if '//' in path else path for path in all_netdirs]
    for subdirtree in set(all_netdirs):
        os.makedirs(subdirtree, exist_ok=True)

    namecache = set()
    for temp_path, net_path, filename in zip(all_paths, all_netdirs, all_names):
        discrete_name = filename not in namecache
        filepath = get_path(filename, root=net_path, overwrite=(overwrite and discrete_name))
        os.rename(temp_path, filepath)
        namecache.add(filename)
