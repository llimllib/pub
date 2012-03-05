from pub import run

for cmd in ["python", "pip", "ls", "rm", "nosetests"]:
    exec """
def %s(cmd, *args, **kwargs):
    return run("%s %%s" %% cmd, *args, **kwargs)""" % (cmd, cmd)
