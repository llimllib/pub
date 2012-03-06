import sys

from sys import exit, stdout, stderr
from os import getcwdu
from imp import load_source
from os.path import abspath, join, isfile

def task(*args, **kwargs):
    def task_decorator(f):
        f.__pub_task__ = True
        f.__pub_dependencies__ = args
        return f
    #If @task is not followed by parens, the function will be the first argument
    if type(args[0]) == type(lambda: 1):
        return task_decorator(args[0])
    #otherwise, return the decorator function, which will be called with the decorated
    return task_decorator

def main(options):
    tasks = []

    if not isfile(options.pubfile):
        print "Unable to find pubfile %s" % abspath(options.pubfile)
        exit(127)

    try:
        #prevent python from writing pubfilec files.
        sys.dont_write_bytecode = True
        pf = load_source("pubfile", options.pubfile)
        sys.dont_write_bytecode = False
    except:
        print "Error in pubfile."
        raise

    #tasks are only those functions which have a __pub_task__ attribute
    tasks = dict((d, getattr(pf, d))
                 for d in dir(pf)
                 if getattr(getattr(pf, d), "__pub_task__", False))

    if options.list_tasks:
        for name, task in tasks.iteritems():
            print "%s: %s" % (name, task.__doc__ if task.__doc__ else "")
        exit()

    if not options.tasks:
        print "no tasks specified. exiting"
        exit(127)

    unknown_tasks = [t for t in options.tasks if t not in tasks.keys()]
    if any(unknown_tasks):
        print "sorry, don't know how to perform tasks %s" % unknown_tasks
        exit()

    for task in options.tasks:
        tasks[task]()
