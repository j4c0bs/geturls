import re
from string import punctuation
from urllib.parse import urlparse
# ------------------------------------------------------------------------------


is_url = re.compile(r"((((http)s?|ftp)://)?(w{3}\.)?([\w\-\.]+)(:\d)?\.([a-z]+)/((\.?(.+[^\/])+(/|\.)?)+)[^\/])$", re.IGNORECASE)


def normalize_url(word, missing_scheme='http'):
    url = urlparse(word)
    if url.scheme:
        if url.scheme in ('http', 'https', 'ftp'):
            norm_scheme = url.scheme
        else:
            if 'f' in url.scheme:
                norm_scheme = 'ftp'
            else:
                norm_scheme = missing_scheme
        host = url.netloc.lower().lstrip(punctuation)
        if host.count('.') >= 2:
            subdomain, domain = host.split('.', 1)
            if set(subdomain) == set('w'):
                host = domain

        norm_path = '/'.join((txt for txt in url.path.split('/') if txt))
        norm_url = '{}://{}/{}'.format(norm_scheme, host, norm_path)
        return norm_url

    else:
        if word.find('/') < word.find('.'):
            word = word[word.find('/')+1:].lstrip(punctuation)
        repair = '{}://{}'.format(missing_scheme, word)
        return normalize_url(repair)


def extract_urls(lines):
    """Parses text for possible URLs.

    Args:
        lines: iterable containing text

    Returns:
        list of validated URLs
    """

    links = []
    for line in lines:
        split_words = (word for word in line.split(' ') if not word.isalnum())
        for word in split_words:
            word = word.lstrip(punctuation)
            valid_url = is_url.search(word)
            if valid_url:
                links.append(normalize_url(valid_url.group()))

    return [link for link in links if link]


def extract_urls_from_files(files):
    """Parses file containing text for possible URLs.

    Args:
        files: iterable containing filepaths

    Returns:
        list of possible URLs
    """

    links = []
    for fn in files:
        with open(fn, 'r') as f:
            lines = [line.strip() for line in f if line.strip() != '']

        found_links = extract_urls(lines)
        if found_links:
            links.extend(found_links)

    if len(links) > 1:
        links = sorted(set(links))

    return links


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    files = sys.argv[1:]
    print()
    links = extract_urls_from_files(files)
    for link in sorted(links, key=lambda u: u.split('://')[1]):
        print(link)
    print()
