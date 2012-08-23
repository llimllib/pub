import sys

from os import getcwdu, chdir
from sys import exit, stdout, stderr
from imp import load_source
from glob import glob
from os.path import abspath, dirname, basename, join, isfile
from itertools import tee, izip, chain

from networkx import DiGraph, simple_cycles, topological_sort

from shortcuts import newer

class DependencyCycle(Exception): pass

def pairwise(iterable):
    """Iterate pairwise through an iterable. Straight from the python docs.

    pairwise([x,y,z]) -> (x,y), (y,z)"""
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

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

    #XXX: Is it important that if a task has "foo" before "bar" as a dep,
    #     that foo executes before bar? Why? ATM this may not happen.

    #Each task that the user has specified gets its own execution graph
    task_graphs = []

    for task in do_tasks:
        exgraph = DiGraph()
        exgraph.add_node(task)
        _get_deps(task, exgraph, dep_graph)

        task_graphs.append(exgraph)

    return flatten(reversed(topological_sort(g)) for g in task_graphs)

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

def unknown_task(f):
    """Run if we can't find the task specified on the cmd line

    Accepts no arguments, just the function to be run."""
    f.__pub_unknown_task__ = True
    return f

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
        pf = load_source("pubfile", basename(options.pubfile))
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

    known_tasks = [t for t in options.tasks if t in tasks.keys()]
    unknown_tasks = [t for t in options.tasks if t not in tasks.keys()]
    if any(unknown_tasks):
        unknown_task_handlers = [getattr(pf, d) for d in dir(pf)
                                 if getattr(getattr(pf, d), "__pub_unknown_task__", False)]
        if unknown_task_handlers:
            for i in range(len(unknown_tasks)):
                #execute the first unknown task handler
                unknown_task_handlers[0]()
        else:
            print "sorry, don't know how to perform tasks %s" % unknown_tasks
            exit(127)

    dep_graph = make_dependency_graph(tasks)

    task_list = get_tasks(known_tasks, dep_graph)

    for task in task_list:
        tasks[task]()
