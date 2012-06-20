#!/usr/bin/env python

#
#  Merge multiple todo.txt style files
#

import sys  # for sys.exit()
from logging import basicConfig, CRITICAL, ERROR, WARNING,\
                                 INFO, debug, DEBUG

from todo import statusDict, parseTodoFile


def merge(filenames):
    "Iterate over files, parsing days, merging, sorting, uniquing"

    # Accumulate all the (no doubt duplicated) tasks
    combinedList = []
    for filename in filenames:
        combinedList += parseTodoFile(filename)

    # For tasks that are the same except for their status,
    # eliminate the less done version.
    taskDict = {}
    for task in combinedList:
        # Put task in a dictionary indexed by dateTime + text
        key = task.string(fixedDate=True, withStatus=False)

        if key in taskDict.keys():
            # Task is already in dictionary so keep only the task with
            # the most finished state.
            oldTask = taskDict[key]
            debug("Dup: %s already in taskDict at %s" % (key, oldTask))
            debug("Old status is %s" % oldTask.status)
            debug("New status is %s" % task.status)
            # statusDict is ordered by doneness.  If the new status is
            # closer to done, replace the older, less done task.
            if statusDict[task.status] > statusDict[oldTask.status]:
                taskDict[key] = task
        else:
            # Haven't seen this one before
            taskDict[key] = task

    # Re-create taskList from the (now unique) dictionary values
    taskList = []
    for task in taskDict.values():
        taskList.append(task)

    # Sort them for printing
    sortedTasks = sorted(taskList, reverse=True)

    # Now print latest version of tasks (print a date on only the
    # tasks from line 0)

    for task in sortedTasks:
        if task.lineNumber == 0:
            print "\n%s" % task.string(color=True)
        else:
            print task.string(withDate=False, color=True)


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
        # FIXME:  basicConfig only works once -- need to make a logger, etc.
        basicConfig(level=verbosity[v], format=f)
    else:
        print "Verbosity should be between 0 and 4, inclusive"
        parser.print_help()
        sys.exit(1)

    debug(args.verbose)
    debug(verbosity[args.verbose])

    merge(args.filenames)
