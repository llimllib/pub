from pub import run
from sys import exit, stdout

for cmd in ["python", "pip", "ls", "rm"]:
    exec """
def %s(cmd, *args, **kwargs):
    return run("%s %%s" %% cmd, *args, **kwargs)""" % (cmd, cmd)
