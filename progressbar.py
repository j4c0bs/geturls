from collections import deque
import os
import time


def byte_unit(n):
    if n // 10**9:
        val = n / 10**9
        unit = 'GB'
    elif n // 10**6:
        val = n / 10**6
        unit = 'MB'
    else:
        val = n / 10**3
        unit = 'KB'
    return '{:.2f}{}'.format(val, unit)



class Progressbar(object):
    def __init__(self, silent):
        self.silent = silent
        self.line_length = os.get_terminal_size()[0]
        self.total = 0
        self.backspace = 0
        self.message = ''
        self.url = ''
        self.set_bar_length()
        self.mkcache = 0
        self.current_total = 0
        self.previous_total = 0
        self.rate = deque([], 5)


    def line_separator(self):
        print('-'*self.line_length)

    def no_byte_headers(self, url):
        print('Downloading URL without byte headers:')
        print(url)


    def set_bar_length(self):
        self.line_length = os.get_terminal_size()[0]
        if self.line_length < 50:
            self.bar_length = int(self.line_length // 2)
        else:
            self.bar_length = self.line_length - 40


    def set_total(self, n):
        self.total = n
        self.display_total = byte_unit(n)
        self.mkcache = 0
        self.current_total = 0
        self.previous_secs = time.time()


    def reset(self, total_bytes=0, url=''):
        self.set_bar_length()
        self.set_total(total_bytes)
        self.url = url


    def draw_bar(self, ix=0):
        a = '['
        marks = '#' * ix
        self.bar = a + marks.ljust(self.bar_length, '-') + '] '


    def draw_display(self, complete=False):
        cum_total = '[{}/{}] '.format(byte_unit(self.current_total), self.display_total)
        line_space = self.line_length - len(cum_total)

        if len(self.url) > line_space + 1:
            trunc_url = self.url[(len(self.url) - line_space) + 5:]
            text_url = '...' + trunc_url
        else:
            text_url = self.url

        url_tot = '{}{}'.format(text_url.ljust(line_space, ' '), cum_total)

        rate_text = self.download_rate()
        bar_tot = '{}{}'.format(self.bar.ljust(self.line_length - len(rate_text), ' '), rate_text)
        text = '\r{}{}'.format(url_tot, bar_tot)
        back = self.line_length * 2
        print(text, end='')

        if not complete:
            print('\b' * back, end='')
        else:
            print('\b' * self.line_length, end='')
            print('-'*self.line_length)


    def download_rate(self):
        kb_delta = (self.current_total - self.previous_total) / 1000
        self.previous_total = self.current_total
        now = time.time()
        secs_delta = now - self.previous_secs
        self.previous_secs = now
        current_rate = kb_delta / secs_delta
        self.rate.append(current_rate)
        rate_text = '[{:.1f} kbps] '.format(sum(self.rate)/len(self.rate))
        return rate_text


    def update(self, chunk_value):
        self.current_total += chunk_value
        if self.total:
            progress = self.current_total / self.total
        else:
            progress = 0

        ix = int(progress * self.bar_length)

        if progress >= 1:
            ix = self.bar_length
            self.draw_bar(ix)
            self.draw_display(complete=True)
        elif ix > self.mkcache:
            self.mkcache = ix
            self.draw_bar(ix)
            self.draw_display()



# ------------------------------------------------------------------------------
if __name__ == '__main__':
    n = 1200
    progressbar = Progressbar()
    progressbar.reset(total_bytes=n, url='test_url.com/ddqdwrfewrfewrfelongfoldernamestoexceed800000000000000000000/file.txt')
    i = 0
    while i < n:
        progressbar.update(100)
        time.sleep(0.2)
        i += 100
