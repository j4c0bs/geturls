from itertools import groupby
import os

from pathname import get_type, get_path, split_name
# ------------------------------------------------------------------------------
def get_duplicates(all_names):
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
    one_file = (len(completed) == 1)
    one_folder = (len(set(all_netdirs)) == 1)

    if not (one_file or one_folder):
        duplicates = get_duplicates(all_names[:])

        if duplicates:
            counter = {fn:0 for fn in duplicates}
            for ix, fn in enumerate(all_names):
                if fn in duplicates:
                    num_suffix = counter.get(fn, 0)
                    name, filetype = split_name(fn)

                    if filetype:
                        filetype = '.' + filetype

                    new_name = ''.join([name, '-', str(num_suffix), filetype])
                    all_names[ix] = new_name
                    counter[fn] += 1

    for filepath, filename in zip(all_paths, all_names):
        real_path, real_name = get_path(filename, overwrite=overwrite)
        os.rename(filepath, real_path)

# ------------------------------------------------------------------------------
