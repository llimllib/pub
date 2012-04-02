pub - the Python Utility Belt
=============================

Pub is a tool to help you automate those tasks you don't want to manually. It
attempts to provide the cleanest, sanest interface for your building, cleaning,
and deploying needs.

Pub code is simply python code, allowing you to leverage the skills and tools
you're already familiar with.

Simply save a `pub.py` file in a dir, import pub, and go on your way.

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