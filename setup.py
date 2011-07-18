# -*- coding: utf-8 -*-
"""
Installs the pyiur Python bindings for the imgur REST API.

"""

import sys

import setuptools

install_requires = [
    'python-dateutil>=1.5,<2.0',
    'requests>=0.5'
]

tests_require = [
]

if sys.version_info < (2, 6):
    install_requires.append('simplejson')

if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setuptools.setup(
    name = 'pyiur',
    version = '0.0.1',
    description = ('Simple Python bindings for the imgur API with account '
                   'support.'),
    keywords = ('imgur image images gallery upload sideload share pic pics '
                'picture pictures'),
    url = 'https://github.com/dcnuno/pyiur',
    download_url = 'git://github.com/dcnuno/pyiur.git',
    platform = ('any',),
    packages = setuptools.find_packages(),
    install_requires = install_requires,
    tests_require = tests_require,
    test_suite = 'tests',
    license = 'License :: OSI Approved :: MIT License',
    classifiers = (
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ),
)
