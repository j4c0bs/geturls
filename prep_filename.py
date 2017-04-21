import os
import re

# ------------------------------------------------------------------------------
def num_sfx(xdir, fn, img_type):
    fn_suffix = 0
    end_digits = [0]
    previous_fn = re.compile(r'^%s_\d{2,}\.%s$' % (fn, img_type.strip('.')))
    for fimg in os.listdir(xdir):
        if previous_fn.match(fimg):
            fn_suffix += 1
            try:
                znum = int(fimg.rsplit('_',maxsplit=1)[1].split('.')[0])
                end_digits.append(znum)
            except ValueError:
                end_digits.append(0)
    max_digit = max(end_digits)
    if max_digit > 0:
        fn_suffix = max_digit + 1
    return '_'+str(fn_suffix).rjust(2, '0')


def prep_filename(xdir, fn, img_type):
    img_num = num_sfx(xdir, fn, img_type)
    if not xdir.endswith(os.sep):
        xdir += os.sep
    return ''.join([xdir, fn, img_num, img_type])

# ------------------------------------------------------------------------------
def get_name(filename, root='.'):
    if '.' not in filename or (filename.startswith('.') and filename.count('.') == 1):
        fn = filename
        fn_type = ''
    else:
        fn, fn_type = filename.rsplit('.', 1)

    check_files = [other_fn for other_fn in os.listdir(root) if fn in other_fn]

    if not check_files:
        pathname = os.path.join(root, filename)

    else:
        fn_incremented = re.compile(r"^%s\-(\d+)\.\w*\d*?$" % (fn))
        end_digits = []
        for other_fn in check_files:
            fn_match = fn_incremented.match(other_fn)
            if fn_match:
                end_digits.append(int(fn_match.groups()))
        if end_digits:
            fn_suffix = str(max(end_digits) + 1)
            fn_out = fn + '-' + fn_suffix + '.' + fn_type
        else:
            fn_out = filename

        pathname = os.path.join(root, fn_out)

    return pathname
