#!/usr/bin/env python

#
#  Merge multiple todo.txt style files
#

import sys  # for sys.exit()
from logging import basicConfig, CRITICAL, ERROR, WARNING,\
                                 INFO, debug, DEBUG
basicConfig(level=INFO, format='%(message)s')

import todo
from todo import statusDict, parseTodoFile


def printTaskList(theList, withLegend=False):
    for task in theList:
        if task.lineNumber == 0:
            print "-----  %s\n" % task.string(useColor=True)
        else:
            print task.string(withDate=False, useColor=True)
    if withLegend:
        # And finally the key
        print todo.statusLegend


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
        key = task.string(withLineNumber=True, fixedDate=True, withStatus=False)

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

    printTaskList(sortedTasks, withLegend=True)


def sweep(fromFile, toFile):
    "Move finished tasks from the first filename to the second."
    todoList = parseTodoFile(fromFile)
    doneList = parseTodoFile(toFile)
    for task in todoList:
        # Move finished tasks
        if task.status in todo.doneStatuses:
            todoList.remove(task)
            doneList.append(task)
        # Copy date lines
        if task.lineNumber == 0:
            doneList.append(task)

    # Now merge the donefile, since it is probably somewhat messed up.
    merge([toFile])


def filesFromDirsAndNames(directory, names):
    """If dir is specified, look for files there.  If not, look in .
    Return list of filenames that existed to merge."""
    import os
    directory = os.path.expanduser(directory)
    result = []
    for name in names:
        name = os.path.expanduser(name)
        if directory:
            longname = "%s/%s" % (directory.rstrip('/'), name)
            debug("Trying %s" % longname)
            if os.path.isfile(longname):
                result.append(longname)
                debug("Worked")
        else:
            if os.path.isfile(name):
                result.append(name)
                debug("Plain filename worked.")

    return result


if __name__ == "__main__":
    import argparse

    files_to_sweep = ["today.txt", "done.txt"]

    parser = argparse.ArgumentParser(description='Sweep finished tasks into a done.txt file')

    parser.add_argument('-d', '--dir', '--directory', default="~/txt/todo")
    parser.add_argument('-v', '--verbose', type=int, default=1)
    parser.add_argument('-n', '-nocolor', type=bool, default=False)
    parser.add_argument('fromfile', nargs='?', default=files_to_sweep[0],
                        help='todo.txt file to sweep from')
    parser.add_argument('tofile', nargs='?', default=files_to_sweep[1],
                        help='done.txt file to sweep info')

    # The object you get back from parse_args() is a 'Namespace'
    # object: An object whose member variables are named after your
    # command-line arguments. The Namespace object is how you access
    # your arguments and the values associated with them:

    args = parser.parse_args()

    verbosity = (CRITICAL, ERROR, WARNING, INFO, DEBUG)
    v = args.verbose
    f = '%(message)s'
    if 0 <= v <= 4:
        # FIXME:  basicConfig only works once -- need to make a logger, etc.
        pass
    else:
        print "Verbosity should be between 0 and 4, inclusive"
        parser.print_help()
        sys.exit(1)

    debug("Verbose = %s", args.verbose)
    debug("Verbosity = %s", verbosity[args.verbose])

    debug("Dir = %s" % args.dir)
    debug("Filename list = %s" % [args.fromfile, args.tofile])

    fileList = filesFromDirsAndNames(args.dir, [args.fromfile, args.tofile])

    sweep(args.fromfile, args.tofile)
