import re
from string import punctuation
# ------------------------------------------------------------------------------

is_url = re.compile(r"(((http)s?://)?(w{3}\.)?([\w\-\.]+)(:\d)?\.([a-z]+)/((\.?(.+[^\/])+(/|\.)?)+)[^\/])$", re.IGNORECASE)
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


def validate_urls(urls):
    valid = []
    for url in urls:
        valid_url = is_url.match(url)
        if valid_url:
            valid.append(check_scheme(valid_url.group()))
    return valid


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


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    lines = ['www.math.wvu.edu/gould/Vol.1.PDF', 'http://www.math.wvu.edu/~gould/Vol.2.PDF', 'http://www.math.wvu.edu/~gould/Vol.3.PDF', 'http://www.math.wvu.edu/~gould/Vol.4.PDF', 'http://www.math.wvu.edu/~gould/Vol.5.PDF', 'http://www.math.wvu.edu/~gould/Vol.6.PDF']

    valid = extract_urls(lines)
    for x in valid:
        print(x)
    # valid = validate_urls(lines)
    # for x in valid:
    #     print(x)
