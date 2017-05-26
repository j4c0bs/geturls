#!/usr/bin/env python3

import argparse
from collections import deque
import os
import time
from time import time as timestamp
# ------------------------------------------------------------------------------
def time_unit(sec):
    if sec >= 3600:
        val = sec / 3600
        unit = 'hrs'
    elif sec >= 60:
        val = sec / 60
        unit = 'min'
    else:
        val = sec
        unit = 'sec'
    return '{:.2f}{}'.format(val, unit)


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


# ------------------------------------------------------------------------------
class Progressbar(object):
    """A class for graphically displaying the progress of a url download.

    ----------------------------------------------------------------------------
    ----------------------------- DISPLAY EXAMPLES -----------------------------
    ----------------------------------------------------------------------------

    --> Standard display:

    (1/5) https://test-url-dot-com/folder_01/file_01.txt       5.90MB : 1.50sec

    (2/5) ...s://test-url-dot-com/folder_002/file_02.txt       6.90MB : 1.77sec

    (3/5) ...://test-url-dot-com/folder_0003/file_03.txt      [  5.41MB/7.90MB]
    [#############################################------------]        3.25MBps

    --> Quiet display:

    (3/12) ...st-url-dot-com/folder_0000000009/file_09.txt    [123.45KB/6.78MB]

    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------

    Attributes:
        - current_fileno: int
            - cumulative total of urls requested
        - nfiles: int
            - total number of urls
        - url: str
            - currently requested url
        - start_time: float
            - timestamp in seconds at start of current url request

    Methods:
        - line_separator
            Prints line of hyphens the full width of the terminal screen
        - no_byte_headers
            Text display for urls without content-length or accept-ranges headers
        - reset
            Entry point for starting download of new url
        - cleanup
            Returns terminal cursor position back to start of screen line
        - timeout
            Returns cursor and prints status
        - update
            Callback for receiving bytes
    """

    def __init__(self, quiet=False, nfiles=1):
        """Instantiate a Progressbar.

        Args:
            quiet: bool - enable quiet mode
            nfiles: int - total number of sequential files / urls
        """

        self._quiet = quiet
        self.current_fileno = 0
        self.nfiles = nfiles
        self._tot_fileno = str(nfiles)
        self._set_update_func(quiet)
        self._line_length = os.get_terminal_size()[0]
        self._set_bar_length()
        self.url = ''
        self.start_time = 0
        self._bytes_tracker = deque([], 256)
        self._seconds_tracker = deque([], 256)
        self._reset_relative_params()


    def line_separator(self):
        print('-'*self._line_length)


    def no_byte_headers(self, url):
        """Display text for URL without valid Accept-Ranges or Content-Length."""

        self.reset(url=url)
        self._complete_switch = True
        fileno_status = '({}/{}) '.format(self.current_fileno, self._tot_fileno)
        notice = '{}Missing byte headers - progress NA: '.format(fileno_status)
        line_space = self._line_length - len(notice)
        text_url = self._truncate_url(line_space)
        header_notice = '{}{}'.format(notice, text_url)
        text = '\r{:<{w}}'.format(header_notice, w=self._line_length)
        print(text, end='')
        if not self._quiet:
            print(' ' * self._line_length)


    def _set_update_func(self, quiet):
        if quiet:
            self.update = self._text_update
        else:
            self.update = self._bar_update


    def _reset_relative_params(self):
        self._complete_switch = False
        self._text_cache = ''
        self._last_ix = 0
        self._current_total = 0
        self._previous_time = timestamp()


    def reset(self, total_bytes=0, url=''):
        """Prepares for downloading new url.

        Args:
            total_bytes: int - size of incoming file in bytes
            url: str - to be displayed in terminal
        """

        if not self._complete_switch and self.current_fileno:
            # print(self._text_cache, end='')
            print(self._text_cache[1:])
            print('Download Incomplete'.center(self._line_length, '*'))
            print('=' * self._line_length)
            # print('-' * self._line_length)

        self.url = url
        self.current_fileno += 1
        self._bytes_total = total_bytes
        self._display_total = byte_unit(total_bytes)
        self._set_bar_length()
        self._reset_relative_params()
        self._bytes_tracker.clear()
        self._seconds_tracker.clear()
        self.start_time = timestamp()


    def cleanup(self):
        if self._quiet:
            print('\b' * self._line_length, end='')


    def timeout(self):
        print('\b' * self._line_length, end='')
        print('CONNECTION TIMEOUT'.center(self._line_length, '-'))


    def _truncate_url(self, line_space):
        """Edits URL to fit line space.

        Args:
            - line_space: int - char space remaining to include running total

        Returns:
            - text_url: str - url to be displayed
        """

        if len(self.url) >= line_space:
            trunc_url = self.url[(len(self.url) - line_space) + 4:]
            text_url = '...' + trunc_url
        else:
            text_url = self.url
        return text_url


    def _running_total(self, complete=False):
        """Constructs url and cumulative total for display.

        Example: https://test-url-dot-com/dir/file  [123.45KB/67.89MB]

        Args:
            - complete: bool - triggers change in display text of current bytes
                to total bytes : total time

        Returns:
            - url_bytes_total: str
        """

        fileno_status = '({}/{}) '.format(self.current_fileno, self._tot_fileno)

        if not complete:
            cur_bytes = '[{}/{}] '.format(byte_unit(self._current_total, pad=True), self._display_total)
        else:
            tot_sec = timestamp() - self.start_time
            cur_bytes = '{} : {} '.format(self._display_total, time_unit(tot_sec))

        line_space = self._line_length - len(cur_bytes) - len(fileno_status)
        text_url = self._truncate_url(self._line_length - 29)
        url_bytes_total = '{}{:<{line_space}}{}'.format(fileno_status, text_url, cur_bytes, line_space=line_space)
        return url_bytes_total


    def _set_bar_length(self):
        """Calculates total len for progress bar based on max size of rate text."""

        self._line_length = os.get_terminal_size()[0]
        self.bar_length = self._line_length - 19


    def _draw_bar(self, ix=0):
        """Creates str progress bar.

        Example: [#########--------]

        Args:
            ix: int - updated progress index for next # character
        """

        marks = '#' * ix
        self.bar = '[{:-<{bar_tot_len}}]'.format(marks, bar_tot_len=self.bar_length)


    def _draw_display(self, ix, complete=False):
        """Creates text for 2 line progress display.

        Args:
            - ix: int
            - complete: bool - Triggers printing single line without backspace.
                Erases current progress bar from display.
        """

        self._draw_bar(ix)
        url_bytes_total = self._running_total(complete=complete)

        rate_text = '{}ps '.format(byte_unit(self.download_rate, pad=True))
        bar_space = self._line_length - len(rate_text)
        bar_total = '{:<{bar_space}}{}'.format(self.bar, rate_text, bar_space=bar_space)
        text = '\r{:<{s}}{:<{s}}'.format(url_bytes_total, bar_total, s=self._line_length)
        back = self._line_length * 2

        self._text_cache = text
        print(text, end='')

        if not complete:
            print('\b' * back, end='')
        else:
            print('\b' * (self._line_length - 1), end='')
            print(' ' * self._line_length)

            # erase in place
            # print('\b' * (self._line_length), end='')


    def _calculate_download_rate(self, bytes_delta):
        """Updates rate for each chunk added as bytes/second."""

        secs_delta = self.current_time - self._previous_time
        self._previous_time = self.current_time
        self._bytes_tracker.append(bytes_delta)
        self._seconds_tracker.append(secs_delta)
        self.download_rate = sum(self._bytes_tracker) / sum(self._seconds_tracker)


    def _update_total(self, chunk_value):
        self.current_time = timestamp()
        self._current_total += chunk_value
        self._calculate_download_rate(chunk_value)


    def _text_update(self, chunk_value):
        """Quiet display - url and cumulative total only.
        Text is not persistent and is erased with each successive call.

        Args:
            chunk_value: int - incoming bytes
        """

        self._update_total(chunk_value)
        url_bytes_total = self._running_total()
        text = '\r{}'.format(url_bytes_total)
        print(text, end='')

        if self._current_total >= self._bytes_total:
            self._complete_switch = True


    def _bar_update(self, chunk_value):
        """Standard 2 line display.

        Arg:
            chunk_value: int - incoming bytes
        """

        self._update_total(chunk_value)
        if self._bytes_total:
            progress = self._current_total / self._bytes_total
        else:
            progress = 0

        ix = int(progress * self.bar_length)

        if ix > self._last_ix and not self._complete_switch:
            if ix >= self.bar_length:
                ix = self.bar_length
                self._draw_display(ix, complete=True)
                self._complete_switch = True
            else:
                self._last_ix = ix
                self._draw_display(ix)


# ------------------------------------------------------------------------------
def simulate_download(nfiles=1, KBps=5000, quiet=False, incomplete=False, overflow=False):
    """Test function to display progressbar.
    File03 simulates a URL without byte headers.
    Filesizes increment in 1MB chunks starting at 4.9MB.

    Args:
        - nfiles: int - number of URLs/files to download
        - KBps: int - simulated download rate
        - quiet: bool - enables quiet display mode
    """

    if incomplete:
        extra_bytes_ratio = 0.8
    elif overflow:
        extra_bytes_ratio = 1.2
    else:
        extra_bytes_ratio = 1


    fake_url = lambda i: 'https://test-url-dot-com/folder_{}/file_{}.txt'.format(str(i).zfill(i+1), str(i).zfill(2))
    filesize = lambda i: (i + 4.9) * 10**6
    progressbar = Progressbar(quiet=quiet, nfiles=nfiles)

    def fake_rate(time_deltas):
        loops_per_sec = 1 / (sum(time_deltas) / len(time_deltas))
        return round((KBps * 1000) / loops_per_sec)

    for i in range(1, nfiles+1):

        if i == 4:
            progressbar.no_byte_headers(url=fake_url(i))
            time.sleep(2)
            continue

        total_bytes = filesize(i)
        progressbar.reset(total_bytes=total_bytes, url=fake_url(i))
        chunk = 1024
        loop_count = 1
        last_time = time.time()
        time_deltas = []
        add_sec = time_deltas.append

        read_bytes = 0
        while read_bytes < total_bytes * extra_bytes_ratio:
            progressbar.update(chunk)
            read_bytes += chunk

            if loop_count % 64 == 0:
                chunk = fake_rate(time_deltas)

            now = time.time()
            add_sec(now - last_time)
            last_time = now
            loop_count += 1

    if quiet:
        progressbar.cleanup()
    else:
        progressbar.reset()

    w = os.get_terminal_size()[0]
    print(' URLs: {} - Completed: {} - Failed: {} '.format(nfiles, nfiles, 0).center(w, '-'))
    print()


# ------------------------------------------------------------------------------
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


def main():
    # import argparse
    args = parse_arguments()

    print('Progressbar simulated file download:\n')
    simulate_download(nfiles=args.nfiles, KBps=args.rate, quiet=args.quiet)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
