import sys

import pub

def make_task(*deps):
    if not deps:
        @pub.task
        def _(): pass
    else:
        @pub.task(*deps)
        def _(): pass
    return _

def test_make_dependency_graph():
    tasks = {"foo": make_task()}
    dep_graph = pub.make_dependency_graph(tasks)

    assert len(dep_graph) == 1
    assert ["foo"] == dep_graph.nodes()
    assert not dep_graph.edges()

def test_simple_dep_graph():
    tasks = {
        "foo": make_task(),
        "bar": make_task("foo")
    }
    dep_graph = pub.make_dependency_graph(tasks)

    assert len(dep_graph) == 2
    assert all(task in dep_graph for task in ["foo", "bar"])
    assert [('bar', 'foo')] == dep_graph.edges()

def test_bigger_dep_graph():
    tasks = {
        "foo": make_task(),
        "bar": make_task("foo"),
        "baz": make_task("foo", "bar"),
    }

    dep_graph = pub.make_dependency_graph(tasks)

    assert len(dep_graph) == 3
    assert all(task in dep_graph for task in ["foo", "bar", "baz"])
    for edge in [('bar', 'foo'), ('baz', 'foo'), ('baz', 'bar')]:
        assert edge in dep_graph.edges()

def test_dep_graph_cycle():
    tasks = {
        "foo": make_task("baz"),
        "bar": make_task("foo"),
        "baz": make_task("bar"),
    }

    try:
        pub.make_dependency_graph(tasks)
        assert 1/0, "Task cycle failed to generate exception"
    except pub.DependencyCycle, err:
        assert "Cycle" in err.message

def test_get_tasks():
    tasks = {
        "foo": make_task(),
        "bar": make_task("foo"),
        "baz": make_task("foo", "bar"),
    }

    dep_graph = pub.make_dependency_graph(tasks)

    tasklist = pub.get_tasks(["baz"], dep_graph)

    assert tasklist == ['foo', 'bar', 'baz'], "Expected [foo, bar, baz], got %s" % (tasklist)

def test_get_tasks2():
    tasks = {
        "foo": make_task(),
        "bar": make_task("foo"),
        "baz": make_task("bar"),
    }

    dep_graph = pub.make_dependency_graph(tasks)

    tasklist = pub.get_tasks(["baz"], dep_graph)

    assert tasklist == ['foo', 'bar', 'baz'], "Expected [foo, bar, baz], got %s" % (tasklist)

def test_get_not_all_tasks():
    tasks = {
        "foo": make_task(),
        "bar": make_task("foo"),
        "baz": make_task("foo"),
    }

    dep_graph = pub.make_dependency_graph(tasks)

    tasklist = pub.get_tasks(["baz"], dep_graph)

    assert tasklist == ["foo", "baz"], "tasklist is: %s" % tasklist

def test_ignore_dupe_edge():
    tasks = {
        "foo": make_task(),
        "bar": make_task("foo"),
        "baz": make_task("bar"),
        "bam": make_task("bar"),
    }
    dep_graph = pub.make_dependency_graph(tasks)

    tasklist = pub.get_tasks(["baz", "bam"], dep_graph)

    assert all(t in tasklist for t in tasks), tasklist
