from shortcuts import make_shortcut, newer

for cmd in ["python", "pip", "ls", "rm", "nosetests", "mkdir", "rsync"]:
    globals()[cmd] = make_shortcut(cmd)
