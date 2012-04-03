from pub import task
from pub.shortcuts import python, pip, rm, nosetests

@task
def clean():
    """clean up the crap left behind by setup.py build"""
    rm("-rf build dist pub.egg-info docs pubfilec")

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
    python("setup.py sdist upload")

@task
def test():
    nosetests("-s")
