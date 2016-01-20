#!/usr/bin/python

import curses, time, sys
from threading import Thread

class PyClock(object):
    kBLOCK = '\033[7m'
    kRESET = '\033[0m'

    # default,grey,red,green,yellow,blue,purple,cyan,white,black
    kCOLORS = [98,90,91,92,93,94,95,96,97,30]

    kHEIGHT_MIN = 1
    kHEIGHT_MAX = 10

    kWIDTH_MIN = 1
    kWIDTH_MAX = 20

    def __init__(self):
        self.needs_update = False
        self._color = None
        self._width = None
        self._height = None

        self.punctuation = True
        self.format = '%I%M%S'
        self.width = self.kWIDTH_MIN
        self.height = self.kHEIGHT_MIN
        self.color = 0

        self.thread = Thread(target = self.run)
        self.running = False

        self.num = None

    @property
    def width(self): return self._width
    @width.setter
    def width(self, value):
        self._width = value
        if self._width < self.kWIDTH_MIN: self._width = self.kWIDTH_MIN
        if self._width > self.kWIDTH_MAX: self._width = self.kWIDTH_MAX
        self.needs_update = True

    @property
    def height(self): return self._height
    @height.setter
    def height(self, value):
        self._height = value
        if self._height < self.kHEIGHT_MIN: self._height = self.kHEIGHT_MIN
        if self._height > self.kHEIGHT_MAX: self._height = self.kHEIGHT_MAX

    @property
    def color(self): return self._color
    @color.setter
    def color(self, value):
        index = int(value)
        val = self.kCOLORS[index]
        self._color = '\033[%sm' % (val)
        self.needs_update = True

    def update(self):
        space = ' '*self.width
        x = self.color+self.kBLOCK+space
        o = self.kRESET+space

        a = x+x+x+x+o
        b = x+o+o+x+o
        c = x+o+o+o+o
        d = o+o+o+x+o
                    # 0,1,2,3,4,5,6,7,8,9
        self.num = [ [a,d,a,a,b,a,a,a,a,a],
                     [b,d,d,d,b,c,c,d,b,b],
                     [b,d,a,a,a,a,a,d,a,a],
                     [b,d,c,d,d,d,b,d,b,d],
                     [a,d,a,a,d,a,a,d,a,a] ]

        self.pun = [o+o,x+o]

        self.needs_update = False

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            if (self.needs_update): self.update()

            cur = [int(k) for k in time.strftime(self.format)]
            length = len(cur)
            punEnd = length - 2
            output = '\n'
            for i in range(5):
                line = '\r ' # needed because of curses
                for j in range(length):
                    line += self.num[i][cur[j]]
                    if self.punctuation and j < punEnd and j % 2 != 0:
                        line += self.pun[i % 2 != 0]

                for k in range(self.height): output += line + "\n"

            sys.stdout.write(output)
            sys.stdout.flush()

            time.sleep(1)

    def toggle_format(self):
        self.format = '%I%M%S' if self.format == '%I%M' else '%I%M'

    def toggle_punctuation(self):
        self.punctuation = not self.punctuation

class Driver(object):
    def __init__(self):
        self.clock = PyClock()
        self.scr = None
        self.quit = True

    def start(self):
        self.quit = False
        self.clock.start()
        self.run()

    def stop(self):
        curses.endwin()
        self.clock.stop()

    def run(self):
        self.scr = curses.initscr()
        curses.cbreak()

        try:
            while self.quit != True:
                key = curses.keyname(self.scr.getch())
                sys.stdout.write('\b \b') # hides character input
                sys.stdout.flush()
                lower = key.lower()

                if lower=='q': self.quit = True
                if lower=='s': self.clock.toggle_format()
                if lower=='p': self.clock.toggle_punctuation()

                if key.isdigit(): self.clock.color = key

                if key==',' or key=='<': self.clock.width -= 1
                if key=='.' or key=='>': self.clock.width += 1

                if key=='[' or key=='{': self.clock.height -= 1
                if key==']' or key=='}': self.clock.height += 1

        except Exception, err:
            print err
        finally:
            self.stop()

if __name__ == '__main__':
    Driver().start()






















