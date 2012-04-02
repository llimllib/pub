pub - the Python Utility Belt
------

Pub is a tool to help you automate those tasks you don't want to manually. It
attempts to provide the cleanest, sanest interface for your building, cleaning,
and deploying needs.

Pub code is simply python code, allowing you to leverage the skills and tools
you're already familiar with.

Simply save a `pub.py` file in a dir, import pub, and go on your way.

Here's an example with two tasks, one to build a project and one to deploy it
to a server:

```python
import pub
from pub.shortcuts import mkdir, cp, rsync

@pub.task
def build():
    mkdir("build")
    cp("src/binary", "build")

@pub.task("build")
def deploy():
    rsync("build", "user@server:~")
```

The pub.shortcuts module gives us handy shortcuts to access command-line
functionality.

The `deploy` task depends on the `build` task, so calling `pub deploy`
will first run the build task, then deploy.
