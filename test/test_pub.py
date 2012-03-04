import os
import pub
import tempfile
from envoy import run

def make_pubfile(pubtext):
    pubfile = tempfile.NamedTemporaryFile()
    pubfile.write(pubtext)
    pubfile.flush()
    return pubfile

def expect(haystack, needle):
    assert needle in haystack, "Couldn't find %s in %s" % (needle, haystack)

def test_task():
    output = []

    sentinel = 'bananas' * 4

    pubtext = """import pub
@pub.task
def foo(): print '%s'""" % sentinel
    
    pf = make_pubfile(pubtext)

    out = run("pub -f %s foo" % (pf.name))
    assert out.status_code == 0
    expect(out.std_out, sentinel)

if __name__ == "__main__":
    test_task()
