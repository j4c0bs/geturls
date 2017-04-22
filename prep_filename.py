import os
import re
from string import punctuation
# ------------------------------------------------------------------------------
char_escape = str.maketrans({p: '\{}'.format(p) for p in punctuation})

def get_name(filename, root='.'):
    if '.' not in filename or (filename.startswith('.') and filename.count('.') == 1):
        fn = filename
        fn_type = ''
    else:
        fn, fn_type = filename.rsplit('.', 1)

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

    pathname = os.path.join(root, fn_out)
    return pathname
