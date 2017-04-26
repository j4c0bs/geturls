from itertools import groupby
import os
import time

from pathname import get_type, get_path
# ------------------------------------------------------------------------------
def get_duplicates(all_names):
    duplicates = []
    all_names.sort(key=get_type)
    for filetype, names in groupby(all_names, get_type):
        namelist = list(names)
        nameset = set(namelist)
        if len(namelist) != len(nameset):
            duplicates.extend([name for name in nameset if namelist.count(name) > 1])

    return duplicates


def to_temp_cwd(all_paths, all_names, duplicates, temp_root):
    tmpcwd = os.path.join(temp_root, str(int(time.time())))
    os.mkdir(tmpcwd)
    updated_paths = []
    updated_names = []
    for temp_path, name in zip(all_paths, all_names):
        new_path, filename = get_path(name, root=tmpcwd, overwrite=(name not in duplicates))
        os.rename(temp_path, new_path)
        updated_paths.append(new_path)
        updated_names.append(filename)

    return updated_paths, updated_names


def to_cwd(completed, temp_root, overwrite):
    all_paths, all_netdirs, all_names = list(zip(*completed))
    one_file = (len(completed) == 1)
    one_folder = (len(set(all_netdirs)) == 1)

    if not (one_file or one_folder):
        duplicates = get_duplicates(all_names[:])
        if duplicates:
            all_paths, all_names = to_temp_cwd(all_paths, all_names, duplicates, temp_root)

    for filepath, filename in zip(all_paths, all_names):
        real_path, real_name = get_path(filename, overwrite=overwrite)
        os.rename(filepath, real_path)

# ------------------------------------------------------------------------------
