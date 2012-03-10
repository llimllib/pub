from os import stat
from sys import stdout, stderr
import envoy

def run(cmd, *args, **kwargs):
    out = envoy.run(cmd, *args, **kwargs)
    if out.status_code > 0:
        stdout.write("error running command: %s\n" % cmd)
        stdout.write(out.std_out)
        stdout.write(out.std_err)
        exit(out.status_code)

    stdout.write(out.std_out) if out.std_out else stderr.write(out.std_err)
    return out

def make_shortcut(cmd):
    """return a function which runs the given cmd
    
    make_shortcut('ls') returns a function which executes
    envoy.run('ls ' + arguments)"""
    def _(cmd_arguments, *args, **kwargs):
        return run("%s %s" % (cmd, cmd_arguments), *args, **kwargs)
    return _

def newer(f1, f2):
    return stat(f1).st_mtime > stat(f2).st_mtime
