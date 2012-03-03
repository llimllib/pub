from envoy import run

for cmd in ["python", "ls", "rm"]:
    exec """
def %s(cmd, *args, **kwargs):
    return run("%s %%s" %% cmd, *args, **kwargs)""" % (cmd, cmd)
