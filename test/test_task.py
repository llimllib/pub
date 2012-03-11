import os
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

def test_file_rule():
    files = []

    #save the current directory so we can return
    curdir = os.path.abspath(os.curdir)

    #move to the test dir so we know where our files are
    os.chdir(os.path.dirname(__file__))
    @pub.file_rule("test_file_rule/*.txt", lambda x: x + ".bak")
    def update_file(f):
        files.append(f)

    #return to the original working dir
    os.chdir(curdir)

    assert files == ['test_file_rule/bananas.txt'], files
