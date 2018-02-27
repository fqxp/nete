#! /usr/bin/env python3
from setuptools import setup
import os.path
import runpy

here = os.path.abspath(os.path.dirname(__file__))

__version__ = runpy.run_module('nete.common.__version__')['__version__']


setup(
    name='nete-common',
    version=__version__,
    description='A note-taking toolset (common modules)',
    author='Frank Ploss',
    author_email='nete@fqxp.de',
    license='GPLv3',
    url='https://github.com/fqxp/nete-backend',
    install_requires=[
        'marshmallow>=3.0.0b7',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-runner',
    ],
    packages=[
        'nete.common',
        'nete.common.models',
        'nete.common.schemas',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
