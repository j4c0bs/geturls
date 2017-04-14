import os
import re
from string import punctuation
from urllib import request
from urllib.error import URLError
# ------------------------------------------------------------------------------

is_url = re.compile(r'^(?:[a-z0-9\.\-\+]*)'
    r'://(?:\S+(?::\S*)?@)'
    r'?(?:(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d))'
    r'{3}|\[[0-9a-f:\.]+\]|'
    r'([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?(?:\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))'
    r'*\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\.?|localhost))(?::\d{2,5})?(?:[/?#][^\s]*)?\Z',
    re.IGNORECASE|re.UNICODE)


def extract_urls(fn):
    links = []
    with open(fn, 'r') as f:
        lines = [line.strip() for line in f if line.strip() != '']

    for line in lines:
        split_words = (word for word in line.split(' ') if not word.isalnum())
        for word in split_words:
            cleaned = word.strip(punctuation)
            if is_url.match(cleaned):
                links.append(cleaned)

    links.sort()
    return links

# ------------------------------------------------------------------------------
def download(file_url):
    try:
        data = request.urlopen(file_url)
    except URLError:
        data = False
    finally:
        return data


def write_data(file_url, subdir=''):
    data = download(file_url)

    if data:

        fn = file_url.rsplit('/', 1)[1]

        if subdir:
            fn = os.path.join(subdir, fn)

        with open(fn, 'wb') as f:
            f.write(data.read())
        return fn

    else:
        return False

# ------------------------------------------------------------------------------

# In [75]: os.system('which wget')
# /usr/local/bin/wget
# Out[75]: 0
# >>> not found -> d == 256
