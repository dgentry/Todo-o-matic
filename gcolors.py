#!/usr/bin/env python

from xtermcolor.ColorMap import XTermColorMap  # , VT100ColorMap
colorz = XTermColorMap().colorize
GREEN = 0x08dd08
AQUA = 0x00ffec
YELLOW = 0xFCD116
RED = 0xdd0606
BLUE = 0x0808dd
AMBER = 0xdd6708
WHITE = 0xdddddd
BRIGHT = 0xffffff
GREY33 = 0x565656
GREY50 = 0x808080
GREY66 = 0xaaaaaa


#following from Python cookbook, #475186
def use_color(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False  # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False
