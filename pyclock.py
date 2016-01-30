#!/usr/bin/python

import curses
from random import randint
from time import strftime
from os import environ

class PyClock(object):
    kPUN_INDEX = 10
    kSQUARE = " "

    def __init__(self, stdscr):
        self._color = None
        self._format = None
        self._width = 0
        self._height = 0

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

        self.running = self.needs_full_update = False

        self.auto_scale = False
        self.center = False
        self.punctuation = True
        self.format = '%I%M%S'

        self.width = 1
        self.height = 1
        self.color = 2

    @property
    def width(self): return self._width
    @width.setter
    def width(self, value):
        window_width = self.stdscr.getmaxyx()[1] - 1

        # output_width
        # =  n_digits * char_width * width + n_puncts * width + (n_spaces - 1) * width
        # = (n_digits * char_width + n_puncts + (n_spaces - 1)) * width
        # => width
        # = output_width / (n_digits * char_width + n_puncts + (n_spaces - 1))

        n_digits = len(self.blank_time)
        n_puncts = 2 if self.punctuation else 0
        n_spaces = n_digits + n_puncts

        u = n_digits * self.char_width + n_puncts + (n_spaces - 1)  # no space for last char
        max_width = window_width // u
        self._width = min(value, max_width)
        self._output_width = self._width * u
        self.needs_full_update = True

    @property
    def height(self): return self._height
    @height.setter
    def height(self, value):
        window_height = self.stdscr.getmaxyx()[0] - 1
        max_height = window_height // self.char_height
        self._height = min(value, max_height)
        self._output_height = self._height * self.char_height
        self.needs_full_update = True

    @property
    def color(self): return self._color
    @color.setter
    def color(self, value):
        index = int(value)
        self._color = curses.color_pair(index if index <= self.color_range+1 else randint(0, self.color_range))
        self.needs_full_update = True

    @property
    def format(self): return self._format
    @format.setter
    def format(self, value):
        self._format = value
        self.blank_time = [None] * len(self.format)
        self.width = self.width # trigger setter

    def update(self):
        cur_time = [int(k) for k in strftime(self.format)]

        if self.needs_full_update:
            self.recalculate_origin()
            self.stdscr.clear()
            self.needs_full_update = False
            self.last_time = self.blank_time
        elif cur_time == self.last_time:
            return

        cur_length = len(cur_time)
        pun_end = cur_length - 2
        full_width = self.char_width*self.width
        space_width = self.width
        x = self.origin_x
        y = self.origin_y

        for i in range(cur_length):
            if self.last_time[i] != cur_time[i]: # skip numbers that haven't changed
                self.draw_number(x, y, cur_time[i])

            x += space_width + full_width

            if self.punctuation and i < pun_end and i % 2 != 0:
                if self.last_time == self.blank_time:
                    self.draw_punctuation(x, y, self.kPUN_INDEX)
                x += space_width + space_width

        self.stdscr.refresh()
        self.last_time = cur_time

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

    def recalculate_origin(self):
        if self.center:
            screen_height, screen_width = self.stdscr.getmaxyx()
            self.origin_x = (screen_width - self._output_width) // 2
            self.origin_y = (screen_height - self._output_height) // 2
        else:
            self.origin_x = 0
            self.origin_y = 0

    def toggle_format(self):
        self.format = '%I%M%S' if self.format == '%I%M' else '%I%M'

    def toggle_punctuation(self):
        self.punctuation = not self.punctuation
        self.width = self.width

    def toggle_center(self):
        self.center = not self.center
        self.needs_full_update = True

    def toggle_auto_scale(self):
        self.auto_scale = not self.auto_scale
        if self.auto_scale: self.view_resized()

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
        curses.halfdelay(10)
        curses.curs_set(0)
        curses.use_default_colors()

        self.clock = PyClock(self.stdscr)
        self.running = False

    def start(self):
        self.running = True
        self.clock.needs_full_update = True
        self.run()

    def run(self):
        while self.running:
            self.clock.update()
            self.update()

    def update(self):
        input = self.stdscr.getch()

        if input == curses.KEY_RESIZE: self.clock.view_resized()

        if input == curses.ERR: return # fix for OSX exiting on terminal window resize
        key = curses.keyname(input)
        lower = key.lower()

        if input==self.kKEY_ESC or lower=='q': self.running = False
        elif lower=='s': self.clock.toggle_format()
        elif lower=='p': self.clock.toggle_punctuation()
        elif lower=='c': self.clock.toggle_center()
        elif lower=='a': self.clock.toggle_auto_scale()

        elif key.isdigit(): self.clock.color = key

        elif key==',' or key=='<': self.clock.change_width(-1)
        elif key=='.' or key=='>': self.clock.change_width( 1)

        elif key=='[' or key=='{': self.clock.change_height(-1)
        elif key==']' or key=='}': self.clock.change_height( 1)

def main(stdscr):
    Driver(stdscr).start()

if __name__ == '__main__':
    environ.setdefault('ESCDELAY', '25')
    curses.wrapper(main)
