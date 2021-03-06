#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for installing geturls.

To install, run:

    python setup.py install

"""

# Modified from https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages

from codecs import open
from os import path
import sys


if sys.argv[-1] == 'setup.py':
    print("To install geturls, run 'python setup.py install'\n")

if sys.version_info[:3] < (3, 4, 3):
    print('geturls requires Python 3.4.3 or later ({}.{}.{} detected)'.format(*sys.version_info[:3]))
    sys.exit(-1)


here = path.abspath(path.dirname(__file__))


setup(
    name='geturls',
    version='1.1.0',
    description='Python tools for parsing, downloading, and organizing URLs',
    long_description=open('README.rst').read(),
    url='https://github.com/JeremyJacobs/geturls',
    author='Jeremy Jacobs',
    author_email='pub@j4c0bs.net',
    license='BSD',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Utilities'
    ],

    keywords='URL requests',
    packages=find_packages(exclude=['docs', '_tests']),
    install_requires=[],
    extras_require={},
    package_data={'':['LICENSE.txt', 'MANIFEST.in', 'docs/*']},
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'geturls=geturls.geturls:main',
            'geturls_simulate=geturls.progressbar:main'
        ],
    },
)
