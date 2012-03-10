import pub

def test_task():
    @pub.task
    def foo(): pass

    assert type(foo) == type(test_task)
    assert foo() is None
    assert foo.__pub_task__ == True
    assert not hasattr(foo, "__pub_dependencies__")

def test_task_with_args():
    @pub.task("foo")
    def foo(): pass

    assert type(foo) == type(test_task)
    assert foo() is None
    assert foo.__pub_task__ == True
    assert foo.__pub_dependencies__ == ("foo",), "foo.__pub_dependencies__ %s" % foo.__pub_dependencies__
