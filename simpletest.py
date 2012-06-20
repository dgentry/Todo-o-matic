#!/usr/bin/env python

#
# Make tests a little cleaner looking
#


from sys import stdout
write = stdout.write

from gcolors import colorz, RED, GREEN, WHITE, BRIGHT

#
# If you are getting this message in your program when you aren't
# running tests, don't import this module unless you ARE running tests.
#

print colorz("Running tests", BRIGHT)

def test(msg, condition):
    write(colorz("%s. . . " % msg, WHITE))
    if condition:
        print colorz("passed", GREEN)
    else:
        print colorz("failed", RED)

