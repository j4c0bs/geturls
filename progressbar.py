import os

# ------------------------------------------------------------------------------
user_msg = {'TEST':'>>> Test message'}

# ------------------------------------------------------------------------------
class Progressbar(object):
    def __init__(self, total, message='', msg0='', msg1=''):
        self.total = total
        self.message = message
        self.msg0 = msg0
        self.msg1 = msg1
        self.back = os.get_terminal_size()[0]
        self.set_length()
        self.mkcache = 0
        self.last = 0
        # print('\n')

    def __call__(self, n):
        self.last += n
        self.update(self.last)


    def welcome(self):
        self.print_message(self.msg0)

    def print_message(self, msg):
        if (msg and (msg in user_msg.keys())):
            print(user_msg[msg])

    def set_length(self):
        if os.get_terminal_size()[0] >= 76:
            self.length = 72
        else:
            self.length = os.get_terminal_size()[0] - 4

    def make_bar(self, ix):
        a = ' ['
        marks = '#' * ix
        self.bar = a + marks.ljust(self.length - 1, '-') + '] '
        self.bar = self.bar.center(self.back, ' ')

    def print_bar(self):
        print(self.bar, end='')
        print('\r' * self.back, end='')

    def update(self, current):
        self.last = current
        progress = current / self.total
        ix = int(progress * self.length)

        if ix == 0:
            self.make_bar(ix)

        elif progress == 1:
            self.make_bar(self.length)
            self.print_bar()
            print()

            if self.msg1:
                self.print_message(self.msg1)
            if self.message:
                print(self.message)

        elif ix > self.mkcache:
            self.make_bar(ix)
            self.print_bar()
            self.mkcache = ix

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    n = 120
    progressbar = Progressbar(n)
    print('\nProgressbar Test\n')
    i = 0
    while i < 130:
        progressbar.update(i)
        i += 7
