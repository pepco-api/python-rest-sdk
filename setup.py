#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from pypep import __version__

setup(
    name='pypep-pepco',
    version=__version__,
    author='Reza Seyf',
    author_email='rseyf@hotmail.com',
    description='Python SDK for Pasargad Internet Payment Gateway',
    license='Apache-2',
    url='https://github.com/pepco-api/python-rest-sdk ',
    packages=['pypep'],
    test_suite='tests',
    tests_require=[
        'httpretty'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache-2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
