from envoy import run
from sys import exit, stdout

def runandprint(cmd, *args, **kwargs):
    out = run(cmd, *args, **kwargs)

    if out.status_code > 0:
        stdout.write("error in command: '%s'\n" % cmd)
        exit(127)

    stdout.write(out.std_out)

for cmd in ["python", "pip", "ls", "rm"]:
    exec """
def %s(cmd, *args, **kwargs):
    return runandprint("%s %%s" %% cmd, *args, **kwargs)""" % (cmd, cmd)
