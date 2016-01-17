#!/bin/python

import curses, time
from threading import Thread

class PyClock(object):
    kBLOCK = '\033[7m'
    kRESET = '\033[0m'

    # default,grey,red,green,yellow,blue,purple,cyan,white,black
    kCOLORS = [98,90,91,92,93,94,95,96,97,30]

    kWIDTH_MIN = 1
    kWIDTH_MAX = 10

    def __init__(self):
        self.needs_update = False
        self._color = None
        self._width = None

        self.width = self.kWIDTH_MIN
        self.color = 0

        self.thread = Thread(target = self.run)
        self.running = False

        self.xxxx = self.xoox = self.xooo = self.ooox = None

    @property
    def width(self): return self._width
    @width.setter
    def width(self, value):
        self._width = value
        if self._width < self.kWIDTH_MIN: self._width = self.kWIDTH_MIN
        if self._width > self.kWIDTH_MAX: self._width = self.kWIDTH_MAX
        self.needs_update = True

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

        self.xxxx = x+x+x+x+o
        self.xoox = x+o+o+x+o
        self.xooo = x+o+o+o+o
        self.ooox = o+o+o+x+o

        self.needs_update = False

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            if (self.needs_update): self.update()

            print '\r\n'*99 + '\n\r'.join(
                [' '.join(
                    [[self.xxxx,self.xoox,self.xooo,self.ooox][int("01110333330302003030110330203002010033330101001030"[int(z)*5+y])]
                        for z in time.strftime("%I%M%S")
                    ]) for y in range(5)
                ]) + '\n', time.sleep(1)

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

                if key=='q': self.quit = True

                if key.isdigit(): self.clock.color = key

                if key==',' or key=='<': self.clock.width -= 1
                if key=='.' or key=='>': self.clock.width += 1

        except Exception, err:
            print err
        finally:
            self.stop()

if __name__ == '__main__':
    Driver().start()






















