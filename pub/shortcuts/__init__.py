from shortcuts import make_shortcut, newer

for cmd in ["python", "pip", "ls", "rm", "nosetests"]:
    globals()[cmd] = make_shortcut(cmd)
