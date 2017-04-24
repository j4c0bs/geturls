import os
import re
from string import punctuation
from urllib.parse import unquote as url_unquote
# ------------------------------------------------------------------------------
char_escape = str.maketrans({p: '\{}'.format(p) for p in punctuation})


def strip_path(url):
    return url.rsplit('/',1)[1]


def get_type(filename, subdir=False):
    if '.' not in filename or (filename.startswith('.') and filename.count('.') == 1):
        fn = filename
        fn_type = '' if not subdir else 'unknown_filetype'
    else:
        fn, fn_type = filename.rsplit('.', 1)
    return fn, fn_type


def get_name(filename, root=os.curdir):
    fn, fn_type = get_type(filename)

    target_dir = os.listdir(root)
    check_files = [other_fn for other_fn in target_dir if fn in other_fn]

    if filename not in target_dir or not check_files:
        fn_out = filename

    else:
        fn_incremented = re.compile(r"^%s\-(\d+)\.%s$" % (fn.translate(char_escape), fn_type))
        end_digits = []

        for other_fn in check_files:
            fn_match = fn_incremented.match(other_fn)
            if fn_match:
                end_digits.append(int(fn_match.groups()[0]))
            elif filename == other_fn:
                end_digits.append(0)

        if end_digits:
            fn_suffix = str(max(end_digits) + 1)
            fn_out = ''.join([fn, '-', fn_suffix, '.', fn_type])
        else:
            fn_out = filename

    filepath = os.path.join(root, fn_out)
    return filepath, fn_out

# >>> change to check_path > input path or root + fn
def url_to_path(url, root=os.curdir):
    filename = strip_path(url)
    filepath = os.path.join(root, filename)
    return filepath, filename


def get_path(url, root=os.curdir, overwrite=False):
    filename = url_unquote(strip_path(url))
    if overwrite:
        filepath = os.path.join(root, filename)
    else:
        filepath, filename = get_name(filename, root)

    return filepath, filename
