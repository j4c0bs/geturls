"""Functions relating to filepaths and filenames.
"""

from difflib import get_close_matches
from itertools import takewhile
import os
import re
import string
# ------------------------------------------------------------------------------
CHAR_ESC = str.maketrans({p: '\{}'.format(p) for p in string.punctuation})


def load_alphamap(split_digits=False):
    alphamap = {}
    if split_digits:
        dig_val = 'd'
    else:
        dig_val = 'a'
    alpha = {a:'a' for a in string.ascii_letters}
    digits = {d:dig_val for d in string.digits}
    punc = {p:'p' for p in string.punctuation}
    for transdict in (alpha, digits, punc):
        alphamap.update(transdict)
    return str.maketrans(alphamap)


ALPHANUM_MAP = load_alphamap()
ALPHA_MAP = load_alphamap(split_digits=True)

# ------------------------------------------------------------------------------
def strip_path(url):
    return url.rsplit('/',1)[1]


def get_type(filename, subdir=True):
    if '.' not in filename or (filename.startswith('.') and filename.count('.') == 1):
        filetype = ''
    else:
        filetype = filename.rsplit('.', 1)[1]
        if any((p in filetype for p in string.punctuation)):
            ft = list(takewhile(lambda s: s.isalnum(), filetype))
            filetype = ''.join(ft)

    if subdir and not filetype:
        filetype = 'unknown_filetype'
    return filetype


def split_name(filename, subdir=False):
    filetype = get_type(filename, subdir=subdir)
    if filetype:
        filename = filename.rsplit('.', 1)[0]

    return filename, filetype


def check_name(filename, root=os.curdir):
    fn, fn_type = split_name(filename)
    target_dir = os.listdir(root)
    check_files = [other_fn for other_fn in target_dir if fn in other_fn]

    if filename not in target_dir or not check_files:
        fn_out = filename
    else:
        fn_incremented = re.compile(r"^%s\-(\d+)\.%s$" % (fn.translate(CHAR_ESC), fn_type))
        end_digits = []

        for other_fn in check_files:
            fn_match = fn_incremented.match(other_fn)
            if fn_match:
                end_digits.append(int(fn_match.groups()[0]))
            elif filename == other_fn:
                end_digits.append(0)

        if end_digits:
            fn_suffix = str(max(end_digits) + 1)
            if fn_type:
                fn_end = '.' + fn_type
            else:
                fn_end = ''
            fn_out = ''.join([fn, '-', fn_suffix, fn_end])
        else:
            fn_out = filename

    filepath = os.path.join(root, fn_out)
    return filepath, fn_out


def get_path(filename, root=os.curdir, overwrite=False):
    if overwrite:
        filepath = os.path.join(root, filename)
    else:
        filepath, filename = check_name(filename, root)

    return filepath, filename


# ------------------------------------------------------------------------------
def char_ix(fn_enc, char='a'):
    """Generator for locating index of specified character within input str.
    
    Args:
        - fn_enc: str - encoded into a/d/p format
        - char: str - character to locate within fn_enc

    Yields:
        - int - index of char within fn_enc
    """

    next_ix = 0
    last_ix = 0
    while next_ix >= 0:
        next_ix = fn_enc.find(char, last_ix)
        if next_ix >= 0:
            yield next_ix
        last_ix = next_ix + 1


def split_to_tokens(filename, minchars=3, split_digits=False):
    """
    Args:
        - filename: str
        - minchars: int - minimum length of token found in filename
        - split_digits: bool - enables splitting alphanumeric str into tokens

    Returns:
        - list: all str tokens sorted by length
    """

    if split_digits:
        STR_MAP = ALPHA_MAP
    else:
        STR_MAP = ALPHANUM_MAP

    fn_enc = filename.translate(STR_MAP)
    alnum_chars = list(char_ix(fn_enc))
    start = [ix for ix in alnum_chars if ix - 1 not in alnum_chars]
    stop = [ix + 1 for ix in alnum_chars if ix + 1 not in alnum_chars]

    str_len = len(fn_enc)
    if split_digits:
        if start[0] != 0:
            start.insert(0, 0)
        if stop[-1] != str_len:
            stop.append(str_len + 1)

    tokens = []
    for start_ix in start:
        for stop_ix in stop:
            token_len = stop_ix - start_ix
            if minchars <= token_len <= str_len:
                tokens.append(filename[start_ix:stop_ix])

    if not split_digits:
        alpha_only = [t for t in tokens if (t.isalnum() and not t.isalpha())]
        for word in alpha_only:
            tokens.extend(split_to_tokens(word, split_digits=True))

    return sorted(tokens, key=lambda s: len(s), reverse=True)


def find_longest_shared_token(group):
    """
    Args:
        - group: iterable of filenames

    Returns:
        - str: longest token that matches all members in group
    """

    all_tokens = []
    for word in group:
        all_tokens.extend(split_to_tokens(word))
    all_tokens = set(all_tokens)
    tracker = []
    for token in all_tokens:
        if all((token in word for word in group)):
            tracker.append(token)

    if not tracker:
        return ''
    else:
        tracker.sort(key=lambda s: len(s), reverse=True)

    return tracker[0]


# ------------------------------------------------------------------------------
def match_names_to_subdirs(filenames):
    """
    Args:
        - filenames: iterable of filenames

    Returns:
        - name_to_subdir: dict - filename to selected subdir based on either
            matching dir name in cwd or token
    """

    matched = set()
    name_to_subdir = {}
    name_sets = {}
    fn_names = set((split_name(fn)[0] for fn in filenames))
    cwd_files = set((f for f in os.listdir() if os.path.isfile(f)))
    cwd_subdirs = [d for d in os.listdir() if os.path.isdir(d)]

    # check against folder names in cwd
    for fn in fn_names:
        check_cwd = get_close_matches(fn, cwd_subdirs)
        if check_cwd:
            name_to_subdir[fn] = check_cwd[0]
            matched.add(fn)

    # find matches within incoming filenames
    fn_names -= matched
    for fn in fn_names:
        if fn in matched:
            continue

        name_matches = get_close_matches(fn, fn_names)

        if len(name_matches) > 1:
            name_sets[fn] = set(name_matches)
            for name in name_matches:
                matched.add(name)
        else:
            # TODO: check group of leftovers for matching tokens
            token_subdir = (0, '')
            fn_tokens = split_to_tokens(fn)
            # TODO: check other tokens if token name is file in cwd
            for token in fn_tokens:
                check_cwd = get_close_matches(token, cwd_subdirs)
                if check_cwd and (len(token) > token_subdir[0]):
                    token_subdir = (len(token), check_cwd[0])

            if token_subdir[0]:
                name_to_subdir[fn] = token_subdir[1]
            else:
                if fn in cwd_files:
                    name_to_subdir[fn] = os.curdir
                else:
                    name_to_subdir[fn] = fn

    # combine groups of matches
    checked = []
    groups = []
    for name_groups in name_sets.values():
        new_set = name_groups.copy()
        for name in name_groups:
            if name in checked:
                continue
            else:
                if name in name_sets:
                    new_set |= name_sets[name]
                groups.append(new_set)
                checked.extend(new_set)

    # use longest token per match group for shared folder name
    for group in groups:
        max_token = find_longest_shared_token(group)
        # TODO: check other tokens
        if not max_token or max_token in cwd_files:
            max_token = os.curdir
        for word in group:
            name_to_subdir[word] = max_token

    return name_to_subdir



# ------------------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------------------
# def get_fake_filelist(d='.'):
#     return [fn for fn in os.listdir(d) if ('.' in fn and not fn.startswith('.'))]

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print()
    test_subdir = '/Users/jpls/Desktop/DLS'
    os.chdir(test_subdir)
    # all_files = get_fake_filelist(d=test_subdir)

    # test_names = ['808DIGIT9', 'numpy-ref-1.12.0', '_a-b.c=d.e_',
    #               'networkx_reference', 'XFCS_Overview', '_test',
    #               'PTA001_m', 'Bleep_01_m01']

    # test_names.sort(key=lambda s: len(s))

    test_names = ['TXT_0.txt', 'URL_TXT_01.txt']

    n = match_names_to_subdirs(test_names)
    print(n)

    # for name in test_names:
    #     print('-'*80)
    #     # print(name)
    #     tokens = split_to_tokens(name)
    #     for t in tokens:
    #         print(t)
