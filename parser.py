import re
from string import punctuation
# ------------------------------------------------------------------------------

is_url = re.compile(r"(((http)s?://)?(w{3}\.)?([\w\-]+)(:\d)?\.([a-z]+)/((\.?(.+[^\/])+(/|\.)?)+)[^\/])$", re.IGNORECASE)
scheme_pattern = re.compile(r"^((http)s?:)?(//).+")
punc = punctuation.replace('/','')

def has_scheme(url):
    if scheme_pattern.match(url):
        return True
    else:
        return False


def check_scheme(url):
    if not has_scheme(url):
        slash_url = '//' + url
        if has_scheme(slash_url):
            url = slash_url
        else:
            return ''

    return url


def extract_urls(lines):
    links = []
    for line in lines:
        split_words = (word for word in line.split(' ') if not word.isalnum())
        for word in split_words:
            word = word.lstrip(punctuation)
            valid_url = is_url.match(word)
            if valid_url:
                links.append(check_scheme(valid_url.group()))

    return [link for link in links if link]
