#! /usr/bin/env python3
from setuptools import setup
import os.path
import runpy

here = os.path.abspath(os.path.dirname(__file__))

__version__ = runpy.run_module('nete.cli.__version__')['__version__']


setup(
    name='nete-cli',
    version=__version__,   # noqa F821
    description='A note-taking toolset (command-line interface)',
    author='Frank Ploss',
    author_email='nete@fqxp.de',
    license='GPLv3',
    url='https://github.com/fqxp/nete-backend',
    install_requires=[
        'python-dateutil>=2.6',
        'requests>=2.18',
        'requests-unixsocket>=0.1',
        'nete-common',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pexpect',
        'pytest',
        'pytest-freezegun',
        'pytest-runner',
        'pytz',
        'requests-mock',
    ],
    packages=[
        'nete.cli',
        'nete.cli.test_utils',
    ],
    entry_points={
        'console_scripts': [
            'nete = nete.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
