#!/usr/bin/env python

#
#  Merge multiple todo.txt style files
#

key =\
"""
Key
-----------------
- to do
x done
> brought forward
/ worked on but not done
. not gonna do (in this form, anyway)
"""

#import io
import os.path
import string

from datetime import datetime, timedelta

from logging import basicConfig, debug, WARNING
#from logging import basicConfig, debug, WARNING
basicConfig(level=WARNING, format='%(message)s')

from g_utils import colorz, YELLOW, WHITE, RED, BRIGHT, GREEN, GREY50


files_to_merge = ["~/txt/todo/today.txt", "~/txt/todo/today-glance3.txt"]


class Task(object):

    def __init__(self):
        self.datetime = None
        self.text = ''
        self.lineNumber = 0


def uniq(aList):
    result = []
    for item in aList:
        if not item in result:
            result.append(item)
        else:
            debug("Uniq'ed out %s" % str(item))
    return result


def datetimeFromString(s):
    import parsedatetime.parsedatetime as pdt

    c = pdt.Calendar()
    result, what = c.parse(s)

    dt = None

    # what was returned (see http://code-bear.com/code/parsedatetime/docs/)
    # 0 = failed to parse
    # 1 = date (with current time, as a struct_time)
    # 2 = time (with current date, as a struct_time)
    # 3 = datetime
    if what in (1, 2):
        # result is struct_time
        dt = datetime(*result[:6])
    elif what == 3:
        dt = datetime(*result[:6])

    if dt is None:
        # Failed to parse
        # raise ValueError, ("Don't understand date '"+s+"'")
        pass  # Jeez, just return None

    return dt


def reasonableDateString(dt):
    """Return the simplest, most human-readable date-time we can.
    For example, if the date/time was "yesterday at 4pm," say that instead of
    "2012-09-11 16:00:00pm"
    """
    now = datetime.now()
    delta = now - dt
    rs = ""
    if delta.days < 1:
        hours = delta.seconds / 3600
        plural = 's' if hours != 1 else ''
        rs += "{} hour{}".format(hours, plural)
        if hours < 8:
            minutes = (delta.seconds - hours * 3600) / 60
            plural = 's' if minutes != 1 else ''
            rs += " {} minute{}".format(minutes, plural)
        rs += " ago"
    elif delta.days < 2:
        rs = dt.strftime("yesterday at %I:%02M %p")
    elif delta.days < 7:
        rs = dt.strftime("last %A at %I:%02M %p")
    else:
        yearstr = "%Y " if dt.year != now.year else ""
        rs = dt.strftime("%d %b {}%I:%M %p".format(yearstr)).strip('0')

    return rs


def parse_one_todo_file(filename):
    """Given a filename, returns a corresponding list of chunks"""
    usable_filename = os.path.expanduser(filename)
    chunks = []

    text = open(usable_filename, "r").readlines()

    # Break file into chunks that begin here and end with a "delimiter
    # line."  Delimiter lines begin with "-----".  Old style ones might
    # have a date on the next line, new ones with the date on the same
    # line

    paragraph = []  # Paragraph is a list of date and lines tuples (today)
    max_date_str = "14 June 2063 23:59:59"
    debug("max_date_str = %s", max_date_str)

    # Start at newest (im)possible date
    last_date_found = datetimeFromString(max_date_str)
    debug("last date = %s", str(last_date_found))

    #
    # Loop through the lines in the file
    #
    for i in range(0, len(text) - 1):
        #debug('%d: %s' % (i, text[i]))

        # '-----' starts a new chunk
        if text[i].startswith('-----'):
            # Finish up the previous chunk
            if len(paragraph) > 0:
                chunks.append((last_date_found, paragraph))

            # Start a new chunk
            paragraph = []
            lineNumber = 0
            s = text[i].strip('- \t\n\r')
            trial_date = datetimeFromString(s)
            if trial_date:
                last_date_found = trial_date
            #debug("trial_date one = %s" % str(trial_date))

        else:  # Text doesn't start with '-----'
            if trial_date == None:  # And we haven't found a date yet
                s = text[i].strip('- \t\n\r')
                trial_date = datetimeFromString(s)
                if trial_date:
                    last_date_found = trial_date
                    #debug("Second line date = %s" % str(trial_date))
                else:
                    last_date_found = last_date_found - timedelta(minutes=1)
                    debug("Using prior last_date_found - 1 min = %s" %\
                          str(last_date_found))
            else:  # trial_date already validly set, normal body line
                paragraph.append((trial_date, lineNumber, text[i].rstrip()))
                lineNumber -= 1

        if string.count(text[i], '<snip>'):
            debug("<snip> Done.")
            break

    for paragraph in chunks:
        debug(colorz(reasonableDateString(paragraph[0]), YELLOW))
        debug(colorz(''.join(repr(paragraph[1])), RED))
    debug("\n\n")

    return chunks


def string_tasktuple(task, withDate=False, withLineNumber=False):
    debug(colorz(task, BRIGHT))

    firstPart = ''
    if withDate:
        firstPart = colorz(reasonableDateString(task[0]), GREEN) + ' '
    if withLineNumber:
        firstPart += colorz(str(task[1]), GREY50) + ' '

    return firstPart + colorz(''.join(task[2]), WHITE)


def merge(files_to_merge):
    "Iterate over files_to_merge, parsing into chunks, merging, sorting, uniquing"
    theList = []
    for filename in files_to_merge:
        theList += parse_one_todo_file(filename)

    # sort the list
    sList = sorted(theList, reverse=True)

    # Uniq it
    uList = uniq(sList)

    # Iterate over the chunks and accumulate a new, flat, task-level list
    flatList = []
    #taskDict = dict()
    for paragraph in uList:
        for task in paragraph[1]:
            debug(string_tasktuple(task))
            flatList.append(task)

    sortedTasks = sorted(flatList, reverse=True)

    uniqueTasks = uniq(sortedTasks)

    # Now print them out (print a date on only the tasks from line 0)
    for task in uniqueTasks:
        if task[1] == 0:
            print string_tasktuple(task, withDate=True)
        else:
            print string_tasktuple(task)

if __name__ == "__main__":
    merge(files_to_merge)
