import sys

from sys import exit, stdout, stderr
from os import getcwdu
from imp import load_source
from os.path import abspath, join, isfile

from networkx import DiGraph, simple_cycles

class DependencyCycle(Exception): pass

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
            assert not dep_graph.has_edge(task, dep), "Cannot add duplicate edge: %s, %s" % (task, dep)
            dep_graph.add_edge(task, dep)

    if simple_cycles(dep_graph):
        raise DependencyCycle("Cycle in the dependency graph: %s" % dep_graph)

    return dep_graph

def get_tasks(tasks, dep_graph):
    task_order = DiGraph()

    for task in tasks:
        if task_order.has_node(task): continue
        task_order.add_node(task)

        def get_deps(task, graph):
            for t in graph.neighbors(task):
                if task_order.has_node(t): continue

                task_order.add_node(task)
                task_order.add_edge(task, t)

                get_deps(t, graph)

        get_deps(task, dep_graph)

    return reversed(topological_sort(task_order))

def task(*args):
    #If we haven't been given any dependencies. Decorate and return.
    if type(args[0]) == type(task):
        args[0].__pub_task__ = True
        return args[0]

    #otherwise, close over args as deps and return a decorator function
    def task_decorator(f):
        f.__pub_task__ = True
        f.__pub_dependencies__ = args
        return f

    return task_decorator

def main(options):
    if not isfile(options.pubfile):
        print "Unable to find pubfile %s" % abspath(options.pubfile)
        exit(127)

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
            print "%s: %s" % (name, task.__doc__ if task.__doc__ else "")
        exit()

    if not options.tasks:
        #TODO: handle default tasks
        print "no tasks specified. exiting"
        exit(127)

    unknown_tasks = [t for t in options.tasks if t not in tasks.keys()]
    if any(unknown_tasks):
        print "sorry, don't know how to perform tasks %s" % unknown_tasks
        exit(127)

    dep_graph = make_dependency_graph(tasks)

    task_list = get_tasks(tasks)

    for task in task_list:
        task()
