import os
import re
import pub
import tempfile
from envoy import run
from nose import with_setup

def change_curdir():
    #change to the directory of this file
    old_curdir = os.getcwdu()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def make_pubfile(pubtext):
    pubfile = tempfile.NamedTemporaryFile()
    pubfile.write(pubtext)
    pubfile.flush()
    return pubfile

def expect(needle, haystack):
    assert re.search(needle, haystack, re.S), "Couldn't find <%s> in <%s>" % (needle, haystack)

def test_task():
    sentinel = 'bananas' * 4

    pubtext = """import pub
@pub.task
def foo(): print '%s'""" % sentinel
    
    pf = make_pubfile(pubtext)

    out = run("pub -f %s foo" % (pf.name))
    assert out.status_code == 0
    expect(sentinel, out.std_out)

def test_help():
    out = run("pub -h")
    txt = out.std_out
    assert out.status_code == 0
    expect('positional arguments', out.std_out)
    expect('optional arguments', out.std_out)

@with_setup(change_curdir)
def test_default_filename():
    """Test that pub executes "pubfile" in this directory when run without
    explicitly specifying a pubfile"""
    out = run("pub foo")
    assert out.status_code == 0
    expect('bananas' * 4, out.std_out)

    #make sure we're not dropping pubfilec files
    assert not os.path.isfile("pubfilec")

def test_no_task_error():
    """Test that pub executes "pubfile" in this directory when run without
    explicitly specifying a pubfile"""
    out = run("pub")
    assert out.status_code == 127
    expect('no tasks specified', out.std_out)

def test_pubfile_error():
    """Test that we see the correct error on an invalid pubfile"""
    pubtext = """1/0"""
    pf = make_pubfile(pubtext)

    out = run("pub -f %s foo" % pf.name)
    assert out.status_code == 1
    expect('Error in pubfile', out.std_out)
    expect('ZeroDivisionError', out.std_err)

def test_pubfile_doesnt_exist():
    out = run("pub -f does_not_exist")

    assert out.status_code == 127
    expect('Unable to find pubfile', out.std_out)
    expect('does_not_exist', out.std_out)

def test_dependencies_simple():
    pubtext = """import pub
@pub.task
def foo(): print 'first'

@pub.task('foo')
def bar(): print 'second'"""
    
    pf = make_pubfile(pubtext)
    out = run("pub -f %s bar" % pf.name)

    assert out.status_code == 0, "got status code %s, stderr: %s" % (out.status_code, out.std_err)
    expect('first.*second', out.std_out)

def test_dont_do_too_much():
    pubtext = """import pub
@pub.task
def foo(): print 'first'

@pub.task('foo')
def bar(): print 'second'"""

    pf = make_pubfile(pubtext)
    out = run("pub -f %s foo" % pf.name)

    assert out.status_code == 0, "got status code %s, stderr: %s" % (out.status_code, out.std_err)
    expect('first', out.std_out)
    assert 'second' not in out.std_out

def test_dont_print_private():
    pubtext = """import pub
@pub.task
def foo(): print 'first'

@pub.task('foo', private=True)
def bar(): print 'second'

@pub.task(private=True)
def baz(): print 'third'"""

    pf = make_pubfile(pubtext)
    out = run("pub -l")

    assert out.status_code == 0, "got status code %s, stderr: %s" % (out.status_code, out.std_err)
    expect('foo', out.std_out)
    assert 'bar' not in out.std_out
    assert 'baz' not in out.std_out

def test_file_rule():
    pubtext = """import pub
@pub.task("mkbar")
def foo(): pass

@pub.file_rule("*.txt", lambda x: x + ".got")
def mkbar(f):
    print f

mkbar('mkbar accepts arguments')"""

    tempdir = tempfile.mkdtemp()
    fname = os.path.join(tempdir, "pub.py")
    open(fname, 'w').write(pubtext)

    pub.shortcuts.touch("%s/test.txt" % tempdir)

    out = run("pub -f %s foo" % fname)

    assert out.status_code == 0, "got status code %s, stderr: %s" % (out.status_code, out.std_err)
    expect('test.txt', out.std_out)
    expect('mkbar accepts arguments', out.std_out)

def test_multiple_tasks():
    sentinel1 = 'alpha' * 4
    sentinel2 = 'beta' * 4

    pubtext = """import pub
@pub.task
def install(): print '%s'

@pub.task
def clean(): print '%s'""" % (sentinel1, sentinel2)

    pf = make_pubfile(pubtext)

    out = run("pub -f %s install clean" % (pf.name))
    assert out.status_code == 0
    expect("%(sentinel1)s.*%(sentinel2)s" % locals(), out.std_out)

def test_multiple_deps():
    pubtext = """import pub
@pub.task("foo", "bar")
def baz(): pass

@pub.task
def foo(): print 'foo'

@pub.task
def bar(): print 'bar'"""

    pf = make_pubfile(pubtext)

    out = run("pub -f %s baz" % (pf.name))
    assert out.status_code == 0, out.std_out + out.std_err
    expect("foo.*bar", out.std_out)

def test_default_action():
    pubtext = """import pub
@pub.task(default=True)
def foo(): print 'foo'"""

    pf = make_pubfile(pubtext)

    out = run("pub -f %s" % (pf.name))
    assert out.status_code == 0, out.std_out + out.std_err
    expect("foo", out.std_out)
