#!/usr/bin/env python

import curses, os
from random import randint
from time import strftime
from argparse import ArgumentParser
from ast import literal_eval

try:    from ConfigParser import RawConfigParser
except: from configparser import RawConfigParser

__program__ = 'PyClock'
__version__ = '1.0.0'
__description__ = 'A digital clock for the terminal'
__author__ = 'Brandon Dreager'
__author_email__ ='pyclock@subol.es'
__copyright__ = 'Copyright (c) 2016 Brandon Dreager'
__license__ = 'MIT'
__website__ = 'https://github.com/Regaerd/PyClock'

# config file detection
config_bases = [os.path.expanduser('~/.')]
try: from xdg.BaseDirectory import xdg_config_home; config_bases.append(xdg_config_home+'/')
except:
    config_bases.append(os.environ.get('XDG_CONFIG_HOME') if os.environ.get('XDG_CONFIG_HOME', None) else os.path.expanduser('~/.config/'))
config_file = 'pyclock.conf'
possible_configs = [dir + config_file for dir in [item for base in config_bases for item in [base, base+'PyClock/']]]
possible_configs.append("{}/{}".format(os.path.dirname(os.path.realpath(__file__)), config_file))

class PyClock(object):
    kPUN_INDEX = 10
    kSQUARE = " "

    kDEFAULT_WIDTH = 1
    kDEFAULT_HEIGHT = 1
    kDEFAULT_COLOR = 2
    kDEFAULT_FORMAT = '%I%M%S'

    def __init__(self, stdscr, clock_args = None):
        self._format = None
        self._width = 0
        self._height = 0
        self._color_index = 0

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
            for i in range(256 if clock_args.color > 10 else 10):
                curses.init_pair(i+1, i, -1)
                self.color_range = i
        except:
            pass

        self.char_height = len(self.templates)
        self.char_width = len(a)

        self.running = self.needs_full_update = False

        self.auto_scale = False
        self.center = False
        self.punctuation = True
        self.format = clock_args.format

        self.width = clock_args.width
        self.height = clock_args.height
        self.color_index = clock_args.color

        if clock_args.auto_scale: self.toggle_auto_scale()
        if clock_args.center: self.toggle_center()
        if not clock_args.punctuation: self.toggle_punctuation()
        if not clock_args.seconds: self.format = self.format.replace('%S', '')

    @property
    def width(self): return self._width
    @width.setter
    def width(self, value):
        window_width = self.stdscr.getmaxyx()[1]

        n_digits = len(self.blank_time)
        n_puncts = 2 if self.punctuation else 0
        n_spaces = n_digits + n_puncts

        u = n_digits * self.char_width + n_puncts + (n_spaces - 1)  # no space for last char
        max_width = window_width // u
        self._width = max(min(value, max_width), 0)
        self._output_width = self._width * u
        self.minimal_mode = self.width * self.height == 0
        self.needs_full_update = True

    @property
    def height(self): return self._height
    @height.setter
    def height(self, value):
        window_height = self.stdscr.getmaxyx()[0]
        max_height = window_height // self.char_height
        self._height = max(min(value, max_height), 0)
        self._output_height = self._height * self.char_height
        self.minimal_mode = self.width * self.height == 0
        self.needs_full_update = True

    @property
    def color_index(self): return self._color_index
    @color_index.setter
    def color_index(self, value):
        self._color_index = 0 if value > self.color_range else self.color_range if value < 0 else value
        self.f_color = curses.color_pair(self._color_index)
        self.b_color = curses.A_REVERSE | self.f_color
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
            self.full_delimiter_width = 1 if self.minimal_mode else self.width*2
            self.full_char_width =  1 if self.minimal_mode else self.char_width*self.width + self.width

            self.stdscr.clear()
            self.needs_full_update = False
            self.last_time = self.blank_time
        elif cur_time == self.last_time:
            return

        cur_length = len(cur_time)
        pun_end = cur_length - 2

        x = self.origin_x
        y = self.origin_y

        for i in range(cur_length):
            if self.last_time[i] != cur_time[i]: # skip numbers that haven't changed
                self.draw_number(x, y, cur_time[i])

            x += self.full_char_width

            if self.punctuation and i < pun_end and i % 2 != 0:
                if self.last_time == self.blank_time:
                    self.draw_punctuation(x, y, self.kPUN_INDEX)

                x += self.full_delimiter_width

        self.stdscr.refresh()
        self.last_time = cur_time

    def draw_number(self, x_origin, y_origin, template_index):
        if self.minimal_mode:
            try: self.stdscr.addstr(y_origin, x_origin, str(template_index), self.f_color)
            except: pass
            return

        y = y_origin
        for r in range(self.char_height):
            line = self.templates[r][template_index]
            length  = len(line)
            for h in range(self.height):
                x = x_origin
                for c in range(length):
                    color = self.b_color if line[c] else 0
                    for w in range(self.width):
                        try: self.stdscr.addstr(y, x, self.kSQUARE, color)
                        except: pass
                        x += 1
                y += 1

    def draw_punctuation(self, x_origin, y_origin, template_index):
        if self.minimal_mode:
            try: self.stdscr.addstr(y_origin, x_origin, ':', self.f_color)
            except: pass
            return

        y = y_origin
        for r in range(self.char_height):
            color = self.b_color if self.templates[r][template_index] else 0
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
            if self.minimal_mode:
                self.origin_x = (screen_width - len(self.blank_time) - (2 if self.punctuation else 0)) // 2
                self.origin_y = screen_height // 2
            else:
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
    kKEY_ESC = '\x1b'
    
    def __init__(self, stdscr, clock_args=None):
        self.stdscr = stdscr
        curses.halfdelay(10)
        curses.curs_set(0)
        curses.use_default_colors()

        self.clock = PyClock(self.stdscr, clock_args)
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
        try:
            key = self.stdscr.getkey()
        except curses.error as e:
            if str(e) == 'no input': return
            raise e

        lower = key.lower()
        if key == 'KEY_RESIZE': self.clock.view_resized()
        elif key==self.kKEY_ESC or lower=='q': self.running = False
        elif lower=='s': self.clock.toggle_format()
        elif lower=='p': self.clock.toggle_punctuation()
        elif lower=='c': self.clock.toggle_center()
        elif lower=='a': self.clock.toggle_auto_scale()

        elif key==',' or key=='<': self.clock.change_width(-1)
        elif key=='.' or key=='>': self.clock.change_width( 1)

        elif key=='[' or key=='{': self.clock.change_height(-1)
        elif key==']' or key=='}': self.clock.change_height( 1)

        elif key.isdigit():        self.clock.color_index = int(key)
        elif key=='-' or key=='_': self.clock.color_index -= 1
        elif key=='=' or key=='+': self.clock.color_index += 1
        elif key=='`' or key=='~': self.clock.color_index = randint(0, self.clock.color_range)

def init_args():
    # arguments
    parser = ArgumentParser(prog=__program__, description=__description__)
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-S', '--no-seconds', action='store_false', default=True,
                        help='do not display seconds', dest='seconds')
    parser.add_argument('-s', '--seconds', action='store_true', default=True,
                        help='display seconds', dest='seconds')
    parser.add_argument('-P', '--no-punctuation', action='store_false', default=True,
                        help='do not display punctuation', dest='punctuation')
    parser.add_argument('-p', '--punctuation', action='store_true', default=True,
                        help='display punctuation', dest='punctuation')
    parser.add_argument('-C', '--no-center', action='store_false', default=True,
                        help='do not center clock display', dest='center')
    parser.add_argument('-c', '--center', action='store_true', default=True,
                        help='center clock display', dest='center')
    parser.add_argument('-A', '--no-auto-scale', action='store_false', default=True,
                        help='do not auto scale display', dest='auto_scale')
    parser.add_argument('-a', '--auto-scale', action='store_true', default=True,
                        help='auto scale display', dest='auto_scale')
    parser.add_argument('-k', '--color', type=int, default=PyClock.kDEFAULT_COLOR, choices=range(256),
                        help='color 0-255 (default: %(default)s)', metavar='COLOR')
    parser.add_argument('-f', '--format', type=str, default=PyClock.kDEFAULT_FORMAT,
                        help='time format (default:%(default)s)', dest='format')
    parser.add_argument('-W', '--width', type=int, default=PyClock.kDEFAULT_WIDTH,
                        help='scale width (default: %(default)s)')
    parser.add_argument('-H', '--height', type=int, default=PyClock.kDEFAULT_HEIGHT,
                        help='scale height (default: %(default)s)')

    # configs
    config = RawConfigParser() # RawConfigParser needed because of time format
    config.read(possible_configs)
    settings = dict(config.items("Settings")) if config.has_section('Settings') else {}

    # fix values that might not be stored correctly (i.e bools)
    for i, item in settings.items(): settings[i] = literal_eval(item)
    parser.set_defaults(**settings)

    return parser.parse_args()

args = init_args()

def main(stdscr=None):
    if not stdscr: curses.wrapper(main)
    else:
        os.environ.setdefault('ESCDELAY', '25')

        try: [int(k) for k in strftime(args.format)]
        except:  args.format = PyClock.kDEFAULT_FORMAT

        Driver(stdscr, clock_args=args).start()

if __name__ == '__main__': main()
