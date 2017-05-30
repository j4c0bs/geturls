import csv
import os

from geturls.dir_tools import confirm_directory, validate_netdir_trees
from geturls.pathname import get_name, get_path, get_type, match_names_to_subdirs
# ------------------------------------------------------------------------------
def to_cwd(completed, overwrite):
    log_details = []

    namecache = set()
    for filepath, url, net_path, filename, dl_timestamp in completed:
        discrete_name = filename not in namecache
        real_path, real_name = get_path(filename, overwrite=(overwrite and discrete_name))
        os.rename(filepath, real_path)
        namecache.add(filename)

        date, clock = dl_timestamp
        log_details.append((date, clock, url, os.path.abspath(real_path)))

    return log_details


# ------------------------------------------------------------------------------
def to_filetype_subdirs(completed, overwrite):
    all_paths, urls, all_netdirs, all_names, all_timestamps = list(zip(*completed))
    fn_types = [get_type(fn, subdir=True) for fn in all_names]
    type_subdirs = sorted(set(fn_types))
    for subdir in type_subdirs:
        confirm_directory(subdir)

    log_details = []
    namecache = set()
    for temp_path, url, filename, filetype, dl_timestamp in zip(all_paths, urls, all_names, fn_types, all_timestamps):
        discrete_name = filename not in namecache
        filepath, filename = get_path(filename, root=filetype, overwrite=(overwrite and discrete_name))
        os.rename(temp_path, filepath)
        namecache.add(filename)

        date, clock = dl_timestamp
        log_details.append((date, clock, url, os.path.abspath(filepath)))

    return log_details


# ------------------------------------------------------------------------------
def to_host_subdirs(completed, overwrite):
    all_paths, urls, all_netdirs, all_names, all_timestamps = list(zip(*completed))

    # >>> setup func to transform netpath to dir friendly
    # >>> >>> combine w validate and return final dir path

    all_netdirs = validate_netdir_trees(all_netdirs)

    log_details = []
    namecache = set()
    for temp_path, url, net_path, filename, dl_timestamp in zip(all_paths, urls, all_netdirs, all_names, all_timestamps):
        discrete_name = filename not in namecache
        filepath, filename = get_path(filename, root=net_path, overwrite=(overwrite and discrete_name))
        os.rename(temp_path, filepath)
        namecache.add(filename)

        date, clock = dl_timestamp
        log_details.append((date, clock, url, os.path.abspath(filepath)))

    return log_details


# ------------------------------------------------------------------------------
def to_name_subdirs(completed, overwrite):
    all_paths, urls, all_netdirs, all_names, all_timestamps = list(zip(*completed))
    name_to_subdir = match_names_to_subdirs(all_names)

    for subdir in set(name_to_subdir.values()):
        if subdir != os.curdir:
            confirm_directory(subdir)

    log_details = []
    namecache = set()
    for temp_path, url, filename, dl_timestamp in zip(all_paths, urls, all_names, all_timestamps):
        discrete_name = filename not in namecache
        subdir = name_to_subdir.get(get_name(filename), os.curdir)
        filepath, filename = get_path(filename, root=subdir, overwrite=(overwrite and discrete_name))
        os.rename(temp_path, filepath)
        namecache.add(filename)

        date, clock = dl_timestamp
        log_details.append((date, clock, url, os.path.abspath(filepath)))

    return log_details


# ------------------------------------------------------------------------------
def to_logfile(logfilename, log_details):
    with open(logfilename, 'a', newline='') as logfile:
        logwriter = csv.writer(logfile)
        logwriter.writerows(log_details)


# ------------------------------------------------------------------------------
