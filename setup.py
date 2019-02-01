#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
import re
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open(os.path.join('fake_cytoscapesearch', '__init__.py')) as ver_file:
    for line in ver_file:
        if line.startswith('__version__'):
            version=re.sub("'", "", line[line.index("'"):])

requirements = [
    'argparse',
    'tzlocal',
    'flask',
    'flask-restplus',
    'Flask-Limiter'
]

setup_requirements = [ ]

test_requirements = [
    'argparse',
    'flask',
    'flask-restplus',
    'unittest2'
]

setup(
    author="Chris Churas",
    author_email='churas.camera@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Fake enrichment",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fake enrichment',
    name='fake_cytoscapesearch',
    packages=find_packages(include=['fake_cytoscapesearch']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/coleslaw481/fake_cytoscapesearch',
    version=version,
    zip_safe=False,
)
