#!/bin/python

import sys, curses, time
from threading import Thread

class PyClock(object):
    kBLOCK = '\033[7m'
    kRESET = '\033[0m'

    # default,grey,red,green,yellow,blue,purple,cyan,white,black
    kCOLOR = [98,90,91,92,93,94,95,96,97,30]

    kWIDTH_MIN = 1
    kWIDTH_MAX = 10

    def __init__(self):
        self.needs_update = False
        self._color = None
        self._width = None
        self._super = 10

        self.width = self.kWIDTH_MIN
        self.color = 0

        self.thread = Thread(target = self.run)
        self.running = False

        self.xxxx = None
        self.xoox = None
        self.xooo = None
        self.ooox = None

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
        val = self.kCOLOR[index]
        self._color = '\033[%sm' % (val)
        self.needs_update = True

    @property
    def super(self): return self._super
    @super.setter
    def super(self, value):
        self._super = value
        print str(self.super)
        self.color = '\033[%sm' % (self.super)
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

if __name__ == '__main__':
    clock = PyClock()
    clock.start()
    print 'started'

    stdscr = curses.initscr()
    curses.cbreak()

    quit=False
    try:
        while quit !=True:
            key = curses.keyname(stdscr.getch())

            if key=='q':
                quit=True
                clock.stop()

            if key.isdigit(): clock.color = key

            if key==',': clock.width -= 1
            if key=='.': clock.width += 1

            if key=='[': clock.super -= 1
            if key==']': clock.super += 1


    except Exception, err:
        print err
        curses.endwin()
        clock.stop()
    finally:
        curses.endwin()
        clock.stop()





















