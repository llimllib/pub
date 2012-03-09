import sys

import pub

def test_make_dependency_graph():
    foo = lambda x: sys.stdout.write("foo")
    foo = pub.task(foo)
    tasks = [foo]
    dep_graph = pub.make_dependency_graph(tasks)

    assert len(dep_graph) == 1
    assert foo == dep_graph.nodes()[0]
