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

        self.auto_scale = False
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
        window_width = self.stdscr.getmaxyx()[1]

        # output_width
        # =  n_digits * char_width * width + n_puncts * width + (n_spaces - 1) * width
        # = (n_digits * char_width + n_puncts + (n_spaces - 1)) * width
        # => width
        # = output_width / (n_digits * char_width + n_puncts + (n_spaces - 1))

        n_digits = len(time.strftime(self.format))
        n_puncts = 2 if self.punctuation else 0
        n_spaces = n_digits + n_puncts

        u = n_digits * self.char_width + n_puncts + (n_spaces - 1)  # no space for last char
        max_width = window_width // u
        self._width = min(value, max_width)
        self._output_width = self._width * u
        self.needs_update = True

    @property
    def height(self): return self._height
    @height.setter
    def height(self, value):
        window_height = self.stdscr.getmaxyx()[0]
        max_height = window_height // self.char_height
        self._height = min(value, max_height)
        self._output_height = self._height * self.char_height
        self.needs_update = True

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

            if self.needs_update:
                self.stdscr.clear()
                self.needs_update = False
                old_time = None
            elif old_time == cur_time:
                time.sleep(0.1)
                continue

            cur_length = len(cur_time)
            pun_end = cur_length - 2
            x = y = 0
            full_width = self.char_width*self.width
            space_width = self.width
            if self.center:
                screen_height, screen_width = self.stdscr.getmaxyx()
                x = (screen_width - self._output_width) // 2
                y = (screen_height - self._output_height) // 2
            for i in range(cur_length):
                if not old_time or old_time[i] != cur_time[i]: # skip numbers that haven't changed
                    self.draw_number(x, y, cur_time[i])

                x += space_width + full_width

                if self.punctuation and i < pun_end and i % 2 != 0:
                    if not old_time:
                        self.draw_punctuation(x, y, self.kPUN_INDEX)
                    x += space_width + space_width

            self.stdscr.refresh()
            old_time = cur_time

            #curses.napms(1000) # doesn't work well/input lag
            #time.sleep(0.01)

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

    def view_resized(self):
        if self.auto_scale:
            # setters will find the maximum width and height
            self.height, self.width = self.stdscr.getmaxyx()
        else:
            self.width = self.width
            self.height = self.height

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

    def toggle_auto_scale(self):
        self.auto_scale = not self.auto_scale
        if self.auto_scale: self.view_resized()
        self.needs_update = True

    def change_width(self, amt):
        self.width += amt
        if self.auto_scale: self.auto_scale = False

    def change_height(self, amt):
        self.height += amt
        if self.auto_scale: self.auto_scale = False


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

                if input == curses.KEY_RESIZE: self.clock.view_resized()

                elif input==self.kKEY_ESC or lower=='q': self.quit = True
                elif lower=='s': self.clock.toggle_format()
                elif lower=='p': self.clock.toggle_punctuation()
                elif lower=='c': self.clock.toggle_center()
                elif lower=='a': self.clock.toggle_auto_scale()

                elif key.isdigit(): self.clock.color = key

                elif key==',' or key=='<': self.clock.change_width(-1)
                elif key=='.' or key=='>': self.clock.change_width( 1)

                elif key=='[' or key=='{': self.clock.change_height(-1)
                elif key==']' or key=='}': self.clock.change_height( 1)

        except:
            pass
        finally:
            self.stop()

def main(stdscr):
    Driver(stdscr).start()

if __name__ == '__main__':
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(main)






















