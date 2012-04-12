from shortcuts import make_shortcut, newer

commands = ["ls", "mkdir", "nosetests", "python",
            "pip", "pub", "rm", "rsync", "touch", "zip"]

for cmd in commands:
    globals()[cmd] = make_shortcut(cmd)

from os import chdir
cd = chdir
