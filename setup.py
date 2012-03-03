#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Thanks to Kenneth Reitz, I stole the template for this

import os
import sys
import pub 

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

required = ['path.py>=2.2', 'envoy>=0.0.2']
packages = ['pub',]

setup(
    name='pub',
    version=pub.__version__,
    description='Python Utility Belt',
    long_description='TODO',
    author='Bill Mill',
    author_email='bill.mill@gmail.com',
    url='https://github.com/llimllib/pub',
    packages=packages,
    package_data={'': ['LICENSE',]},
    include_package_data=True,
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
