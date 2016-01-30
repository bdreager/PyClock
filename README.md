# PyClock

###What
A simple digital clock for the terminal

###Run
```
python pyclock.py
```
###Controls

Keys  | Actions
----- | -------
<kbd>q</kbd> or <kbd>Q</kbd> | quit
<kbd>s</kbd> or <kbd>S</kbd> | toggle seconds
<kbd>p</kbd> or <kbd>P</kbd> | toggle punctuation
<kbd>c</kbd> or <kbd>C</kbd> | toggle center display
<kbd>a</kbd> or <kbd>A</kbd> | toggle auto scale display
<kbd>0</kbd> to <kbd>9</kbd> | change color
<kbd><</kbd> or <kbd>,</kbd> | decrease width
<kbd>></kbd> or <kbd>.</kbd> | increase width
<kbd>[</kbd> or <kbd>{</kbd> | decrease height
<kbd>]</kbd> or <kbd>}</kbd> | increase height

###Command-line options

Options | Descriptions
------- | ------------
`-h` or `--help` | show help message
`-S` or `--no-seconds` | do not display seconds
`-P` or `--no-punctuation` | do not display punctuation
`-C` or `--no-center` | do not center clock display
`-A` or `--no-auto-scale` | do not auto scale display
`-c COLOR` or `--color COLOR` | color 0-9 (default: 2)
`-W WIDTH` or `--width WIDTH` | scale width (default: 1)
`-H HEIGHT` or `--height HEIGHT` | scale height (default: 1)

###Support

- [x] Works on Linux completely

- [x] Works on OSX completely

- [ ] Will not work on Windows due to special characters
######Windows support is a very low priority
