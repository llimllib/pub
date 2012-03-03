import envoy
from sys import exit, stdout

def task(f):
    f.__pub_task__ = True
    return f

def run(cmd, *args, **kwargs):
    out = envoy.run(cmd, *args, **kwargs)
    if out.status_code > 0:
        stdout.write("error running command: %s" % cmd)
        exit(out.status_code)

    stdout.write(out.std_out)
