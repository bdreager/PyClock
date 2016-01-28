#!/usr/bin/python

import curses, time, sys, os
from random import randint
from threading import Thread

class PyClock(object):
    # kBLOCK = '\033[7m'
    # kRESET = '\033[0m'
    # kCLEAR = '\033[2J\033[;H'
    kPUN_INDEX = 10
    kSQUARE = " "

    # default,grey,red,green,yellow,blue,purple,cyan,white,black
    # kCOLORS = [98,90,91,92,93,94,95,96,97,30]

    # kHEIGHT_MIN = 1
    # kHEIGHT_MAX = 10

    # kWIDTH_MIN = 1
    # kWIDTH_MAX = 20

    def __init__(self, stdscr):
        self.stdscr = stdscr

        x = True
        o = False

        a = [x,x,x,x]
        b = [x,o,o,x]
        c = [x,o,o,o]
        d = [o,o,o,x]
                          # 0,1,2,3,4,5,6,7,8,9,:
        self.templates = [ [a,d,a,a,b,a,a,a,a,a,o],
                           [b,d,d,d,b,c,c,d,b,b,x],
                           [b,d,a,a,a,a,a,d,a,a,o],
                           [b,d,c,d,d,d,b,d,b,d,x],
                           [a,d,a,a,d,a,a,d,a,a,o] ]

        # some linux terminals throw an exception after 7, but osx supports all 10
        try:
            for i in range(10):
                curses.init_pair(i, -1, i)
                self.color_range = i
        except:
            pass

        self.char_height = len(self.templates)
        self.char_width = len(a)

        self.running = False
        self.needs_update = True

        self._color = None
        self._width = None
        self._height = None

        self.center = False
        self.punctuation = True
        self.format = '%I%M%S'
        self.width = 1 # self.kWIDTH_MIN
        self.height = 1 # self.kHEIGHT_MIN
        self.color = 2

    @property
    def width(self): return self._width
    @width.setter
    def width(self, value):
        self._width = value
        if self._width < 0: self._width = 0
        # if self._width < self.kWIDTH_MIN: self._width = self.kWIDTH_MIN
        # if self._width > self.kWIDTH_MAX: self._width = self.kWIDTH_MAX
        self.needs_update = True

        num = len(time.strftime(self.format))
        output_width = num * (self.char_width*self.width + self.width)
        if self.punctuation: output_width += (self.width + self.width)*2
        
        window_width = self.stdscr.getmaxyx()[1]

        if output_width > window_width: self.width -= 1 #trigger setter

    @property
    def height(self): return self._height
    @height.setter
    def height(self, value):
        self._height = value
        if self._height < 0: self._height = 0
        # if self._height < self.kHEIGHT_MIN: self._height = self.kHEIGHT_MIN
        # if self._height > self.kHEIGHT_MAX: self._height = self.kHEIGHT_MAX
        self.needs_update = True

        output_height = self.char_height * self.height + (self.height*2)
        window_height = self.stdscr.getmaxyx()[0]

        if output_height > window_height: self.height -= 1 #trigger setter

    @property
    def color(self): return self._color
    @color.setter
    def color(self, value):
        index = int(value)
        self._color = curses.color_pair(index if index <= self.color_range+1 else randint(0, self.color_range))
        self.needs_update = True

    def start(self):
        self.running = True
        self.thread = Thread(target = self.run)
        self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        self.needs_update = True
        while self.running:
            cur_time = [int(k) for k in time.strftime(self.format)]
            if self.needs_update or cur_time != old_time:
                self.needs_update = False
                self.stdscr.clear()
                self.stdscr.refresh()
                old_time = None
            else:
                time.sleep(0.01)
                continue

            cur_length = len(cur_time)
            pun_end = cur_length - 2
            x = y = 0
            full_width = self.char_width*self.width
            space_width = self.width
            if self.center:
                screen_height, screen_width = self.stdscr.getmaxyx()
                output_width = cur_length * (self.char_width*self.width + self.width)
                if self.punctuation: output_width += (self.width + self.width)*2
                x = (screen_width + 1 - output_width) // 2
                y = (screen_height + 1 - (self.char_height * self.height)) // 2
            for i in range(cur_length):
                if not old_time or old_time[i] != cur_time[i]: # skip numbers that haven't changed
                    self.draw_number(x, y, cur_time[i])

                x += space_width + full_width

                if self.punctuation and i < pun_end and i % 2 != 0:
                    self.draw_punctuation(x, y, self.kPUN_INDEX)
                    x += space_width + space_width

            self.stdscr.refresh()
            old_time = cur_time

            #curses.napms(1000) # doesn't work well/input lag
            time.sleep(0.01)

    def draw_number(self, x_origin, y_origin, template_index):
        y = y_origin
        for r in range(self.char_height):
            line = self.templates[r][template_index]
            length  = len(line)
            for h in range(self.height):
                x = x_origin
                for c in range(length):
                    color = self.color if line[c] else 0
                    for w in range(self.width):
                        self.stdscr.addstr(y, x, self.kSQUARE, color)
                        x += 1
                y += 1

    def draw_punctuation(self, x_origin, y_origin, template_index):
        y = y_origin
        for r in range(self.char_height):
            color = self.color if self.templates[r][template_index] else 0
            for h in range(self.height):
                x = x_origin
                for w in range(self.width):
                    self.stdscr.addstr(y, x, self.kSQUARE, color)
                    x += 1
                y += 1

    def toggle_format(self):
        self.format = '%I%M%S' if self.format == '%I%M' else '%I%M'
        self.width = self.width # trigger setter
        self.needs_update = True

    def toggle_punctuation(self):
        self.punctuation = not self.punctuation
        self.width = self.width
        self.needs_update = True

    def toggle_center(self):
        self.center = not self.center
        self.needs_update = True

class Driver(object):
    kKEY_ESC = 27
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        #curses.start_color()
        curses.use_default_colors()

        self.clock = PyClock(self.stdscr)
        self.quit = True

    def start(self):
        self.quit = False

        self.clock.start()
        curses.napms(100) #needed for a race condition

        self.run()

    def stop(self):
        self.clock.stop()

    def run(self):
        try:
            while self.quit != True:
                input = self.stdscr.getch()
                key = curses.keyname(input)
                lower = key.lower()

                if input == curses.KEY_RESIZE:
                    self.clock.width = self.clock.width
                    self.clock.height = self.clock.height

                elif input==self.kKEY_ESC or lower=='q': self.quit = True
                elif lower=='s': self.clock.toggle_format()
                elif lower=='p': self.clock.toggle_punctuation()
                elif lower=='c': self.clock.toggle_center()

                elif key.isdigit(): self.clock.color = key

                elif key==',' or key=='<': self.clock.width -= 1
                elif key=='.' or key=='>': self.clock.width += 1

                elif key=='[' or key=='{': self.clock.height -= 1
                elif key==']' or key=='}': self.clock.height += 1

        except Exception, err:
            print err
        finally:
            self.stop()

def main(stdscr):
    Driver(stdscr).start()

if __name__ == '__main__':
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(main)






















