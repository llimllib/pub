import sys

from os import getcwdu, chdir
from sys import exit, stdout, stderr
from imp import load_source
from glob import glob
from os.path import abspath, dirname, join, isfile
from itertools import tee, izip

from networkx import DiGraph, simple_cycles, topological_sort

from shortcuts import newer

class DependencyCycle(Exception): pass

def pairwise(iterable):
    """Iterate pairwise through an iterable. Straight from the python docs.

    pairwise([x,y,z]) -> (x,y), (y,z)"""
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def make_dependency_graph(tasks):
    dep_graph = DiGraph()

    #build the dependency graph in two steps. First add the nodes
    for task in tasks:
        assert not dep_graph.has_node(task), "Cannot add duplicate task: %s" % task
        dep_graph.add_node(task)

    #then add the edges.
    taskdeps = [(name, task.__pub_dependencies__)
                 for name, task in tasks.iteritems()
                 if hasattr(task, "__pub_dependencies__")]
    for task, deps in taskdeps:
        for dep in deps:
            dep_graph.add_edge(task, dep)

    #now, to assure that a task with deps "foo", "bar" executes foo before bar,
    #go through each task and add a dep from bar -> foo
    for name, task in tasks.iteritems():
        if hasattr(task, "__pub_dependencies__") and len(task.__pub_dependencies__) > 1:
            for task1, task2 in pairwise(task.__pub_dependencies__):
                dep_graph.add_edge(task2, task1)

    if simple_cycles(dep_graph):
        raise DependencyCycle("Cycle in the dependency graph: %s" % dep_graph)

    return dep_graph

def _get_deps(task, task_graph, dep_graph):
    for t in dep_graph.neighbors(task):
        #if we already have node t in the task graph, we can just add an edge
        #from the current node and move on to the next neighbor, as we must have
        #the dependncy chain above t in the graph.
        if task_graph.has_node(t):
            task_graph.add_edge(task, t)
            continue

        #otherwise, add the node and recurse on it
        else:
            task_graph.add_node(t)
            task_graph.add_edge(task, t)

            _get_deps(t, task_graph, dep_graph)

def get_tasks(do_tasks, dep_graph):
    """Given a list of tasks to perform and a dependency graph, return the tasks
    that must be performed, in the correct order"""
    task_order = DiGraph()
    dep_graph = dep_graph.copy()

    #first add dependencies between the tasks to perform,
    #to make sure that we run the tasks in the order given
    #on the cmd line. "pub install clean" needs a dep
    #clean -> install. This dep is ephemeral, so we operate
    #on a copy of the dep graph
    for task1, task2 in pairwise(do_tasks):
        dep_graph.add_edge(task2, task1)

    for task in do_tasks:
        task_order.add_node(task)
        _get_deps(task, task_order, dep_graph)

    return list(reversed(topological_sort(task_order)))

def needed(f1, f2):
    return not isfile(f2) or newer(f1, f2)

#return a function which closes over a filelist and a function to construct the
#name of a new file, which:
#  returns a function which closes over the function used to generate a new file,
#  which:
#     returns an argument-less function that actually applies the file rule
def file_rule(filelist, name_func):
    def f(build_file):
        def g(f=None):
            #called with 0 arguments, build all files in the filelist
            if not f:
                for fname in glob(filelist):
                    if needed(fname, name_func(fname)):
                        build_file(fname)
            #called with 1 argument, build that file
            else:
                build_file(f)

        g.__pub_task__ = True
        g.__pub_dependencies__ = ()
        g.__pub_options__ = {"private": True}

        return g
    return f

#XXX accept kwargs and add private kwarg
def task(*args, **kwargs):
    #If we haven't been given any dependencies. Decorate and return.
    if args and type(args[0]) == type(task):
        f = args[0]
        f.__pub_task__ = True
        f.__pub_options__ = kwargs
        return f

    #otherwise, close over args as deps and return a decorator function
    def task_decorator(f):
        f.__pub_task__ = True
        f.__pub_dependencies__ = args
        f.__pub_options__ = kwargs
        return f

    return task_decorator

def main(options):
    #if the user has not specified a pubfile, try a few defaults
    if options.pubfile is None:
        defaults = ["pub.py", "pubfile.py"]

        for f in defaults:
            if isfile(f):
                options.pubfile = f

        if not options.pubfile:
            print "Unable to find pub.py"
            exit(127)

    if not isfile(options.pubfile):
        print "Unable to find pubfile %s" % abspath(options.pubfile)
        exit(127)

    #insert the pubfile's dir at the front of sys.path
    sys.path.insert(0, dirname(abspath(options.pubfile)))

    #run in the directory containing the pubfile
    chdir(dirname(abspath(options.pubfile)))

    try:
        #prevent python from writing pubfilec files.
        sys.dont_write_bytecode = True
        #TODO: scan an array of pubfile name options
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
            if not task.__pub_options__.get("private"):
                print "%s: %s" % (name, task.__doc__ if task.__doc__ else "")
        exit()

    if not options.tasks:
        #search for an action marked default
        options.tasks = []
        for name, task in tasks.iteritems():
            if task.__pub_options__.get("default"):
                options.tasks.append(name)

        #if tasks is *still* empty, fail out
        if not options.tasks:
            print "no tasks specified. exiting"
            exit(127)

    unknown_tasks = [t for t in options.tasks if t not in tasks.keys()]
    if any(unknown_tasks):
        print "sorry, don't know how to perform tasks %s" % unknown_tasks
        exit(127)

    dep_graph = make_dependency_graph(tasks)

    task_list = get_tasks(options.tasks, dep_graph)

    for task in task_list:
        tasks[task]()
