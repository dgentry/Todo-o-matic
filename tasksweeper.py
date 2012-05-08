#!/usr/bin/env python

print "Whee."

import io
import os.path
import sys
import string
import colorama
from colorama import Fore, Back, Style
colorama.init()
from termcolor import colored

filename = os.path.expanduser("~/txt/todo/today.txt")

lines = []
days = []
tasklist = ()

text = open(filename, "r").readlines()

for line in text:
    if string.count(line, '<snip>'):
        sys.exit(0)
    if line[0:5] == '-----':
        date = line[6:].strip()
        tasklist = ()
        sys.stdout.write(colored("\nDate: %s\n" % date, 'white', \
                                 attrs=['bold']))
    else:
        status = line.strip()
        if len(status):
            status = status[0]
            color = None
            style = None
            if status == '-':
                color = 'yellow'; style=['bold']
            elif status == 'x':
                color = 'grey'; style=None

            if color:
                sys.stdout.write(colored(line, color, attrs=style))
            else:
                sys.stdout.write(line)
        
        


if __name__ == "__main__":

    print 'main here.'
    print days
    
