import re
from string import punctuation
# ------------------------------------------------------------------------------

is_url = re.compile(r"(((http)s?://)?(w{3}\.)?([\w\-\.]+)(:\d)?\.([a-z]+)/((\.?(.+[^\/])+(/|\.)?)+)[^\/])$", re.IGNORECASE)
scheme_pattern = re.compile(r"^((http)s?:)?(//).+")
punc = punctuation.replace('/','')


def _has_scheme(url):
    if scheme_pattern.match(url):
        return True
    else:
        return False


def _check_scheme(url):
    if not _has_scheme(url):
        slash_url = '//' + url
        if _has_scheme(slash_url):
            url = slash_url
        else:
            return ''

    return url


def validate_urls(urls):
    valid = []
    for url in urls:
        valid_url = is_url.match(url)
        if valid_url:
            valid.append(_check_scheme(valid_url.group()))
    return valid


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
            valid_url = is_url.match(word)
            if valid_url:
                links.append(_check_scheme(valid_url.group()))

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
