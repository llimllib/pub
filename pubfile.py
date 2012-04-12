from pub import task
from pub.shortcuts import make_shortcut, python, pip, rm, nosetests

@task
def clean():
    """clean up the crap left behind by setup.py build"""
    rm("-rf build dist pub.egg-info docs setup.pyc")

@task
def build():
    """build pub"""
    python("setup.py build")

@task
def install():
    """install pub"""
    python("setup.py install")

@task
def reinstall():
    """uninstall and reinstall pub; probably only useful for developers"""
    pip("uninstall -y pub")
    install()

@task
def publish():
    """upload pub to pyPI"""
    pandoc = make_shorcut("pandoc")

    pandoc("-s -w rst README.md -o README.rs")
    python("setup.py sdist upload")
    rm("README.rs")

@task
def test():
    """run pub's tests"""
    nosetests("-s")
