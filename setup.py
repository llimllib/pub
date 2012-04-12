#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Thanks to Kenneth Reitz, I stole the template for this

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

required = ['path.py>=2.2', 'envoy>=0.0.2', 'networkx>=1.6']
packages = ['pub', 'pub.shortcuts']

#skip README.rs if it hasn't been generated, it's only important
#on publication to pyPI. The pubfile generates it from README.md
try:
    longdesc = open("README.rs").read()
except:
    longdesc = ''

setup(
    name='pub',
    version='0.0.4',
    description='Python Utility Belt',
    long_description=longdesc,
    author='Bill Mill',
    author_email='bill.mill@gmail.com',
    url='https://github.com/llimllib/pub',
    packages=packages,
    scripts = ['pub/bin/pub'],
    package_data={'': ['LICENSE',]},
    include_package_data=True,
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
