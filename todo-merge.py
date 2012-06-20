#!/usr/bin/env python

#
#  Merge multiple todo.txt style files
#

import os.path
import string
from operator import itemgetter, attrgetter
from datetime import datetime, timedelta
import logging
from logging import basicConfig, CRITICAL, ERROR, warn, WARNING,\
                                 info, INFO, debug, DEBUG
basicConfig(level=INFO, format='%(message)s')

from g_utils import colorz, YELLOW, WHITE, RED, BRIGHT, GREEN, GREY50


def uniq(aList):
    result = []
    for item in aList:
        if not item in result:
            result.append(item)
        else:
            pass  #debug("Uniq'ed out %s" % str(item.__dict__))
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
    """Return the clearest, most human-readable date-time we can.
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
        rs += dt.strftime(" ago (%I:%M %p)")
    elif delta.days < 2:
        rs = dt.strftime("yesterday at %I:%M %p")
    elif delta.days < 7:
        rs = dt.strftime("last %A at %I:%M %p")
    else:
        yearstr = "%Y " if dt.year != now.year else ""
        rs = dt.strftime("%d %b {}%I:%M %p".format(yearstr)).strip('0')

    return rs


def fixedDateString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


key =\
"""
----------<snip>-----------

Key
-----------------
- to do
x done
> brought forward
/ worked on but not done
. not gonna do (in this form, anyway)
"""
statusDict = {
    '' : 0,  #  '',
    '-': 1,  #  'to do',
    '>': 2,  #  'forwarded',
    '/': 3,  #  'worked on & forwarded',
    '.': 4,  #  'no',
    'x': 5   #  'done'
}

class Task(object):

    def __init__(self, newDateTime=None, newLineNumber=0, newText='', newStatus=''):
        self.dateTime = newDateTime
        self.lineNumber = newLineNumber
        self.status = newStatus

        # Throw away whitespace and newlines at end of all lines
        newText = newText.rstrip(' \t\r\n')
        self.text = newText

        # If there's still something left of the text, maybe there's a status
        if len(newText) > 0:
            potentialStatus = newText.lstrip(' \t')[0]  # first nonspace char
            if potentialStatus in statusDict.keys():
                # Line started with a status, don't include status or
                # whitespace in text
                self.status = potentialStatus
                # Save text without status, but don't lose indentation
                self.text = newText.replace(self.status, '', 1)


    def __eq__(self, other):
        return self.dateTime == other.dateTime and self.text == other.text \
               and self.status == other.status

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.dateTime < other.dateTime or \
            (self.dateTime == other.dateTime and \
             self.lineNumber < other.lineNumber)

    def __le__(self, other):
        return self.__le__(other) or self.__eq__(other)
    
    def __gt__(self, other):
        return self.dateTime > other.dateTime or \
            (self.dateTime == other.dateTime and \
             self.lineNumber > other.lineNumber)
    
    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)
    
    def string(self, withDate=True, fixedDate=False, withStatus=True,
               withLineNumber=False, color=False):
        firstPart = ''
        if color:
            colrz = colorz
        else:
            colrz = lambda string, color: string
        if withDate:
            if fixedDate:
                dateStrFn = fixedDateString
            else:
                dateStrFn = reasonableDateString
            firstPart = colrz(dateStrFn(self.dateTime), GREEN) + ' '
        if withLineNumber:
            firstPart += colrz(str(self.lineNumber), GREY50) + ' '

        if withStatus:
            status = self.status
        else:
            status = ''

        return firstPart + status + colrz(''.join(self.text), WHITE)


def parse_one_todo_file(filename):
    """Given a filename, returns a corresponding list of (not uniqued) tasks"""
    usable_filename = os.path.expanduser(filename)
    taskList = []

    text = open(usable_filename, "r").readlines()

    # Break file into chunks that begin here and end with a "delimiter
    # line."  Delimiter lines begin with "-----".  Old style ones might
    # have a date on the next line, new ones with the date on the same
    # line

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
            # Start a new dated chunk
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
                task = Task(last_date_found, lineNumber, text[i])
                taskList.append(task)
                lineNumber -= 1

        if string.count(text[i], '<snip>'):
            debug("<snip> Done.")
            break

    return taskList



def merge(files_to_merge):
    "Iterate over files_to_merge, parsing days, merging, sorting, uniquing"
    debug(files_to_merge)
    combinedList = []
    for filename in files_to_merge:
        combinedList += parse_one_todo_file(filename)

    # sort the list
    sortedTasks = sorted(combinedList, reverse=True)

    # Uniq it
    #uniqueTasks = uniq(sortedTasks)
    uniqueTasks = uniq(sortedTasks)

    # Now, for tasks that are the same except for their status,
    # eliminate the less done version.

    # Put them in a dictionary indexed by dateTime + text
    taskDict = {}
    cleanedUpTasks = []
    for task in uniqueTasks:
        key = task.string(fixedDate=True, withStatus=False)

        # If task (except status) is already in dictionary, keep most
        # finished state.

        if key in taskDict.keys():
            oldTask = taskDict[key]
            debug("Whoa, %s already in taskDict at %s" % (key, oldTask))
            debug("Old status is %s" % oldTask.status)
            debug("New status is %s" % task.status)
            # If the new one is closer to done, replace the more done one
            if statusDict[oldTask.status] < statusDict[task.status]:
                taskDict[key] = task
        else:
            taskDict[key] = task

        taskList = []
        for task in taskDict.values():
            taskList.append(task)

        sortedTasks = sorted(taskList, reverse=True)
        uniqueTasks = uniq(sortedTasks)

    # Now print latest version of tasks (print a date on only the
    # tasks from line 0)

    for task in uniqueTasks:
        if task.lineNumber == 0:
            print("")
            print(task.string(color=True))
        else:
            print(task.string(withDate=False, color=True))


if __name__ == "__main__":
    import argparse

    files_to_merge = ["~/txt/todo/today.txt", "~/txt/todo/today-glance3.txt"]

    parser = argparse.ArgumentParser(description='Merge some todo.txt files')

    parser.add_argument('-d', '--directory', default='~/txt/todo')
    parser.add_argument('-v', '--verbose', type=int, default=1)
    parser.add_argument('-D', '--done-file', default='~/txt/todo/done.txt')
    parser.add_argument('filenames', nargs='?', default=files_to_merge,
                        help='todo.txt files to merge')

    # The object you get back from parse_args() is a 'Namespace'
    # object: An object whose member variables are named after your
    # command-line arguments. The Namespace object is how you access
    # your arguments and the values associated with them:

    args = parser.parse_args()
    if len(args.filenames) < 2:
        print "Need two (or more) files to merge."
        parser.print_help()
        sys.exit(1)

    verbosity = (CRITICAL, ERROR, WARNING, INFO, DEBUG)
    v = args.verbose
    f = '%(message)s'
    if 0 <= v <= 4:
        basicConfig(level=verbosity[v], format=f)
    else:
        print "Verbosity should be between 0 and 4, inclusive"
        parser.print_help()
        sys.exit(1)

    debug(args.verbose)
    debug(verbosity[args.verbose])

    merge(args.filenames)
