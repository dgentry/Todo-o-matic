#!/usr/bin/env python

#
#  Merge (dated) tasks from multiple todo.txt style files
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

#from logging import basicConfig, info, debug, DEBUG, warn, WARNING
from logging import basicConfig, debug, DEBUG
basicConfig(level=DEBUG, format='%(message)s')

from g_utils import colorz, YELLOW, WHITE  # , RED, GREEN, BRIGHT


files_to_merge = ["~/txt/todo/today.txt", "~/txt/todo/today-glance3.txt"]


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


def merge():
    chunks = dict()
    for filename in files_to_merge:
        fn = os.path.expanduser(filename)

        chunks[filename] = []

        text = open(fn, "r").readlines()
        # Break file into chunks that begin here and end with a "delimiter line"

        # Delimiter lines begin with "-----".  Old style ones might have a
        # date on the next line, new ones with the date on the same line

        timechunk = []  # Timechunk is a list of date and lines tuples (today)
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
                if len(timechunk) > 0:
                    chunks[filename].append((last_date_found, timechunk))

                # Start a new chunk
                timechunk = []
                s = text[i].strip('- \t\n\r')
                trial_date = datetimeFromString(s)
                if trial_date:
                    last_date_found = trial_date
                debug("trial_date one = %s" % str(trial_date))

            else:  # Text doesn't start with '-----'
                if trial_date == None:  # And we haven't found a date yet
                    s = text[i].strip('- \t\n\r')
                    trial_date = datetimeFromString(s)
                    if trial_date:
                        last_date_found = trial_date
                        debug("Second line date = %s" % str(trial_date))
                    else:
                        last_date_found = last_date_found - timedelta(minutes=1)
                        debug("Using prior last_date_found - 1 min = %s" %\
                              str(last_date_found))
                else:  # trial_date already validly set
                    timechunk.append((trial_date, text[i].rstrip() + '\n'))

            if string.count(text[i], '<snip>'):
                debug("<snip> Done.")

    # If debugging, print out what we have without merging, uniquing or sorting
    for filename in chunks:
        for timechunk in chunks[filename]:
            debug(colorz(reasonableDateString(timechunk[0][0]), YELLOW))
            debug(colorz(''.join(timechunk[1]), WHITE))
        debug("\n\n")

    # make one list
    theList = chunks[files_to_merge[0]] + chunks[files_to_merge[1]]
    sList = sorted(theList, reverse=True)

    # Uniq it
    uList = []
    for x in sList:
        if not x in uList:
            uList.append(x)
        else:
            print "Uniq'ed out %s", x

    print len(uList)

    # Output the chunks
    for timechunk in uList:
        print colorz(reasonableDateString(timechunk[0]), YELLOW)
        print colorz(''.join(timechunk[1]), WHITE)


if __name__ == "__main__":
    merge()
