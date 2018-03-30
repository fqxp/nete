#! /usr/bin/env python3
from setuptools import setup
import os.path
import runpy

here = os.path.abspath(os.path.dirname(__file__))

__version__ = runpy.run_module('nete.backend.__version__')['__version__']


setup(
    name='nete-backend',
    version=__version__,   # noqa F821
    description='A note-taking toolset (backend)',
    author='Frank Ploss',
    author_email='nete@fqxp.de',
    license='GPLv3',
    url='https://github.com/fqxp/nete-backend',
    install_requires=[
        'aiohttp>=3.1',
        'marshmallow>=3.0.0b7',
        'nete-common',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'aioreloader',
        'pexpect',
        'pytest',
        'pytest-aiohttp',
        'pytest-asyncio',
        'pytest-freezegun',
        'pytest-runner',
    ],
    packages=[
        'nete.backend',
        'nete.backend.storage',
        'nete.backend.storage.filesystem',
    ],
    entry_points={
        'console_scripts': [
            'nete-backend = nete.backend.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
