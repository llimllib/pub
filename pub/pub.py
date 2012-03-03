#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from os import getcwdu
from os.path import abspath, join
from path import path

def main(options):
    root = path(getcwdu())
    try:
        pubfile = open(root / "pubfile")
    except IOError:
        print "unable to find pubfile"

    tasks = []

    def task(f):
        tasks.append(f)

    try:
        eval(pubfile)
    except:
        print "Error in pubfile. TODO: print sys_exc or whatevers"

    tasks[0]()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Python Utility Belt v0.1')

    args = parser.parse_args()

    main(args)
