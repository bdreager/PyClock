#!/usr/bin/python

import curses, time, sys
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

            cur = [int(k) for k in time.strftime("%I%M%S")]
            length = len(cur)
            punEnd = length - 2
            output = '\n'
            for i in range(5):
                line = '\r' # needed because of curses
                for j in range(length):
                    line += self.num[i][cur[j]]
                    if j < punEnd and j % 2 != 0:
                        line += self.pun[i % 2 != 0]

                output += line + "\n"

            sys.stdout.write(output)

            time.sleep(1)

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

                if key.lower()=='q': self.quit = True

                if key.isdigit(): self.clock.color = key

                if key==',' or key=='<': self.clock.width -= 1
                if key=='.' or key=='>': self.clock.width += 1

        except Exception, err:
            print err
        finally:
            self.stop()

if __name__ == '__main__':
    Driver().start()






















