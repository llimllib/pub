pub - the Python Utility Belt
=============================

`pub` is a tool to help you automate those tasks you don't want to do manually.
It attempts to provide the cleanest, sanest interface for your building, 
cleaning, and deploying needs.

Pub code is simply python code, allowing you to leverage the skills and tools
you're already familiar with.

Simply install `pub`, save a `pub.py` file in a dir, and start coding.

Here's an example pub.py with two tasks, one to build a project and one to
deploy it to a server:

```python
from pub import task
from pub.shortcuts import mkdir, cp, rsync

@task
def build():
    mkdir("build")
    cp("src/binary", "build")

@task("build")
def deploy():
    rsync("build", "user@server:~")
```

The pub.shortcuts module gives us handy shortcuts to access command-line
functionality.

The `deploy` task depends on the `build` task, so calling `pub deploy`
will first run the build task, then deploy.

Installation
------------

`pip install pub`

Tasks
-----

The `task` decorator in the pub module will be your code's main interface
to pub.

You may create a task with no arguments:

```python
from pub import task

@task
def zomg():
    print "omgbbq"
```

If you run `pub zomg` on a pub.py file containing this function, you will
see "omgbbq" printed out.

You may also create a task with arguments. Each argument should be the name
of another function. The functions in the argument list will all be executed
before your task.

For example:

```python
from pub import task

@task
def foo():
    print "foo"

@task("foo")
def bar():
    print "bar"

@task("foo", "bar")
def baz():
    print "baz"
```

If you run `pub foo`, you will see "foo".

If you run `pub bar`, you will see "foo" followed by "bar".

If you run `pub baz`, you will see "foo" followed by "bar" followed by "baz".

Dependencies will be resolved left-to-right, meaning that there's an implied
dependency of each item in a dependency list on its left-hand neighbor. Be
careful that you don't create a circular dependency like so:

```python
from pub import task

@task
def foo():
    print "foo"

@task("foo")
def bar():
    print "bar"

@task("bar", "foo")
def baz():
    print "baz"
```

In this case, `bar` depends on `foo` by the definition of `bar`, but `foo`
depends on `bar` by the definition of `baz`. Pub will be confused about this
situation, and resolve it by quitting out with an error.

There are two legal keywords you can use with the task decorator: `private`
and `default`. `private` just means that `pub -l` won't list your task; if 
you have a `pub.py` file like:

```python
from pub import task

@task(private=True)
def private_func(): pass
```

and you run `pub -l`, which normally lists all tasks, `private_func` will not
be listed.

`default` marks the task as a default action. If you have a `pub.py` like:

```python
from pub import task

@task(default=True)
def do_something(): print "got here"
```

and run `pub` with no arguments, you should see "got here" printed.

You may mark any number of tasks as `default`; they will all be run if `pub`
is invoked without arguments. While their dependency information will never
be ignored, there is no defined order in which they will be run.

Tasks are documented simply by giving them docstrings. Given this `pub.py`:

```python
from pub import task

@task
def gotit():
    """You've got it!"""
    pass

@task
def noyou():
    """I thought you had it."""
    pass
```

We can see how they are displayed by pub:

```
$ pub -l
gotit: You've got it!
noyou: I thought you had it.
```

There is one special task decorator, `@unknown_task`. This task will be run
once for each task pub is given that it doesn't know how to run. That is, if
you have a pubfile:


```
from pub import task, unknown_task

@task
def foo(): print "foo"

@unknown_task
def bar(): print "bar"
```

And run the command `pub zot` on that pubfile, pub will print `bar`. If you
run `pub zot zip`, it will print `bar\nbar`.

Shortcuts
---------

The `pub.shortcuts` module builds on @kennethreitz's fine
[envoy](https://github.com/kennethreitz/envoy) module to provide a convenient
command-line interface for pub.

You can see all the commands that are available
[in the source](https://github.com/llimllib/pub/blob/master/pub/shortcuts/__init__.py),
or you can make your own:

```python
from pub.shortcuts import make_shortcut

gcc = make_shortcut("gcc")

#then use it like so:
gcc("-o guildenstern.exe rosencrantz.c")
```

The invocation of the `gcc` funciton at the end will translate into 
`gcc -o guildenstern.exe rosencrantz.c` and be run.

We can also use our shortcuts to inspect the input, output, and status
code of the command;
the return value of a shortcut will be an
[envoy](https://github.com/kennethreitz/envoy) result. Check their
documentation for specifics, but basically you can see its output with:

```python
from pub.shortcuts import make_shortcut

echo = make_shortcut("echo")

out = echo("A conspiracy of cartographers")

assert out.std_out == "A conspiracy of cartographers\n"
```

The `pub.shortcuts` module also contains one utility function, `newer`. It
simply accepts two arguments and returns True if the mtime of the first is
newer than the mtime of the second. Its entire defintion follows:

```python
def newer(f1, f2):
    return stat(f1).st_mtime > stat(f2).st_mtime
```

The `pub` command
-----------------

The pub command is best described by its `--help` output:

```
usage: pub [-h] [-l] [-f FILE] [task [task ...]]

Python Utility Belt v0.0.4

positional arguments:
  task                  the tasks to run

optional arguments:
  -h, --help            show this help message and exit
  -l                    list available tasks
  -f FILE, --pubfile FILE 
                        The file to use as a pubfile
```

Contributing
------------

Please do! Patches and issues will be gladly accepted.

To run `pub`'s tests, just run `pub test`; you'll need to have installed
[nose](https://github.com/nose-devs/nose) first.
