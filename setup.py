#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='ManuCostModel',
    version='0.0.1',
    packages=find_packages(include=['ManuCostModel', 'ManuCostModel.*']),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'webcolors'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)

