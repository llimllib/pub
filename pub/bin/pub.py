#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from os import getcwdu
from imp import load_source
from os.path import abspath, join

from path import path

def main(options):
    root = path(getcwdu())
    try:
        pubfile = open(root / "pubfile")
    except IOError:
        print "unable to find pubfile"

    tasks = []

    try:
        pf = load_source("pubfile", "pubfile")
    except:
        print "Error in pubfile. TODO: print sys_exc or whatevers"

    tasks = [getattr(pf, d) for d in dir(pf) if getattr(getattr(pf, d), "__pub_task__", False)]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Python Utility Belt v0.1')

    args = parser.parse_args()

    main(args)
