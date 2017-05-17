import csv
# from itertools import groupby
import os
from dir_tools import confirm_directory
from pathname import get_type, get_path, split_name
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
    all_netdirs = [path.split('//')[1] if '//' in path else path for path in all_netdirs]
    for subdirtree in set(all_netdirs):
        os.makedirs(subdirtree, exist_ok=True)

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
def to_logfile(logfilename, log_details):
    with open(logfilename, 'a', newline='') as logfile:
        logwriter = csv.writer(logfile)
        logwriter.writerows(log_details)
