#!/usr/bin/env python3

from collections import deque
import os
import time
from time import time as timestamp
# ------------------------------------------------------------------------------
def byte_unit(n, pad=False):
    if n >= 10**9:
        val = n / 10**9
        unit = 'GB'
    elif n >= 10**6:
        val = n / 10**6
        unit = 'MB'
    else:
        val = n / 10**3
        unit = 'KB'
    if pad:
        return '{:>6.2f}{}'.format(val, unit)
    else:
        return '{:.2f}{}'.format(val, unit)


# def average(iterable):
#     return sum(iterable) / len(iterable)


class Progressbar(object):
    def __init__(self, quiet):
        self._set_update_func(quiet)
        self.quiet = quiet
        self.line_length = os.get_terminal_size()[0]
        self._set_bar_length()
        self._url = ''
        self._complete_switch = False
        self.total = 0
        self.mkcache = 0
        self.current_total = 0
        self.previous_total = 0
        self.bytes_tracker = []
        self.seconds_tracker = []
        self.bytes_tracker = deque([], 256)
        self.seconds_tracker = deque([], 256)

        if not quiet:
            print('{:>{n}}'.format(time.ctime(), n=self.line_length - 1))

    def _set_update_func(self, quiet):
        if quiet:
            self.update = self._text_update
        else:
            self.update = self._bar_update

    def line_separator(self):
        print('-'*self.line_length)

    def no_byte_headers(self, url):
        print('Downloading URL without byte headers:')
        print(url)

    def set_total(self, n):
        self.total = n
        self.display_total = byte_unit(n)
        self.mkcache = 0
        self.previous_total = 0
        self.current_total = 0
        self.previous_time = timestamp()
        self.bytes_tracker.clear()
        self.seconds_tracker.clear()

    def reset(self, total_bytes=0, url=''):
        self._set_bar_length()
        self.set_total(total_bytes)
        self._url = url
        self._complete_switch = False

    def cleanup(self):
        print('\b' * self.line_length, end='')
        # print('-' * self.line_length)

    def timeout(self):
        print('\b' * self.line_length, end='')
        print('CONNECTION TIMEOUT'.center(self.line_length, '-'))

    def _truncate_url(self, line_space):
        # if len(self._url) > line_space - 1:
        if len(self._url) >= line_space:
            trunc_url = self._url[(len(self._url) - line_space) + 5:]
            text_url = '...' + trunc_url
        else:
            text_url = self._url
        return text_url

    def _running_total(self):
        cur_bytes_total = '[{}/{}] '.format(byte_unit(self.current_total, pad=True), self.display_total)
        line_space = self.line_length - len(cur_bytes_total)
        # text_url = self._truncate_url(line_space)
        text_url = self._truncate_url(self.line_length - 25)
        # url_bytes_total = '{}{}'.format(text_url.ljust(line_space, ' '), cur_bytes_total)
        url_bytes_total = '{:<{line_space}}{}'.format(text_url, cur_bytes_total, line_space=line_space)
        return url_bytes_total


    def _set_bar_length(self):
        """4 space char pad bar and rate text == 17 char total
           rate text --> 12 + 1 char max
        """

        self.line_length = os.get_terminal_size()[0]
        self.bar_length = self.line_length - 17

    def _draw_bar(self, ix=0):
        """Creates str progress bar.
           [#########--------]
           Shares line space with rate text. e.g. [123.45KBps]
        """

        a = '['
        marks = '#' * ix
        self.bar = a + marks.ljust(self.bar_length, '-') + '] '

    def _draw_display(self, ix, complete=False):
        self._draw_bar(ix)
        url_bytes_total = self._running_total()
        rate_text = '[{}ps] '.format(byte_unit(self.download_rate, pad=True))
        # bar_total = '{}{}'.format(self.bar.ljust(self.line_length - len(rate_text), ' '), rate_text)

        bar_total = '{:<{bar_space}}{}'.format(self.bar, rate_text, bar_space=self.line_length - len(rate_text))
        text = '\r{}{}'.format(url_bytes_total, bar_total)
        back = self.line_length * 2
        print(text, end='')

        if not complete or self._complete_switch:
            print('\b' * back, end='')
        else:
            print('\b' * self.line_length, end='')
            print('-'*self.line_length)

    def _calculate_download_rate(self, bytes_delta):
        secs_delta = self.current_time - self.previous_time
        self.previous_time = self.current_time

        self.bytes_tracker.append(bytes_delta)
        self.seconds_tracker.append(secs_delta)
        self.download_rate = sum(self.bytes_tracker) / sum(self.seconds_tracker)

    def _update_total(self, chunk_value):
        self.current_time = timestamp()
        self.current_total += chunk_value
        self._calculate_download_rate(chunk_value)

    def _text_update(self, chunk_value):
        self._update_total(chunk_value)
        url_bytes_total = self._running_total()
        text = '\r{}'.format(url_bytes_total)
        print(text, end='')

    def _bar_update(self, chunk_value):
        self._update_total(chunk_value)
        if self.total:
            progress = self.current_total / self.total
        else:
            progress = 0

        ix = int(progress * self.bar_length)

        if progress >= 1:
            ix = self.bar_length
            # if not self._complete_switch:
            self._draw_display(ix, complete=True)
            self._complete_switch = True
        elif ix > self.mkcache:
            self.mkcache = ix
            self._draw_display(ix)


# ------------------------------------------------------------------------------
def fake_download(nfiles=1, KBps=5000, quiet=False):
    fake_url = lambda i: 'https://test-url-dot-com/folder_{}/file_{}.txt'.format(str(i).zfill(i+1), str(i).zfill(2))
    filesize = lambda i: (i + 4.9) * 10**6
    progressbar = Progressbar(quiet)
    # chunk_loops = []

    def fake_rate(time_deltas):
        loops_per_sec = 1 / (sum(time_deltas) / len(time_deltas))
        return round((KBps * 1000) / loops_per_sec)

    for i in range(nfiles):
        total_bytes = filesize(i)
        progressbar.reset(total_bytes=total_bytes, url=fake_url(i))
        chunk = 1024
        loop_count = 1
        last_time = time.time()
        time_deltas = []
        add_sec = time_deltas.append

        read_bytes = 0
        while read_bytes < total_bytes:
            progressbar.update(chunk)
            read_bytes += chunk

            if loop_count % 64 == 0:
                chunk = fake_rate(time_deltas)

            now = time.time()
            add_sec(now - last_time)
            last_time = now
            loop_count += 1

        # chunk_loops.append((chunk, round(1 / (sum(time_deltas) / len(time_deltas)))))

    if quiet:
        progressbar.cleanup()

    print(' URLs: {} - Completed: {} - Failed: {} '.format(nfiles, nfiles, 0).center(progressbar.line_length, '-'))
    print()
    # for (cx, x) in chunk_loops:
    #     print('loops_per_sec: {}  ||  faked download rate: {}'.format(x, byte_unit(cx * x)))


def parse_arguments():
    parser = argparse.ArgumentParser(prog='progressbar - test',
                                     description='test display of progressbar')

    parser.add_argument('--nfiles', '-n', type=int, default=5,
                         help='Number of simulated files to download - defaults to 5')

    parser.add_argument('--rate', '-r', type=int, default=5000,
                         help='Simulated download rate (KBps) - defaults to 5000')

    parser.add_argument('--quiet', '-q', action='store_true',
                         help='Minimal status display to stdout')

    return parser.parse_args()


if __name__ == '__main__':
    import argparse
    args = parse_arguments()

    print('Progressbar simulated file download:\n')
    fake_download(nfiles=args.nfiles, KBps=args.rate, quiet=args.quiet)
