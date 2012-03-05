from shortcuts import make_shortcut

for cmd in ["python", "pip", "ls", "rm", "nosetests"]:
    globals()[cmd] = make_shortcut(cmd)
