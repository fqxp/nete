#! /usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='nete',
    version='0.1',
    author='Frank Ploss',
    author_email='nete@fqxp.de',
    license='GPL',
    url='https://github.com/fqxp/nete-backend',
    install_requires=[
        'aiohttp',
        'python-dateutil',
        'requests',
        'requests-unixsocket',
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
        'requests-mock',
    ],
    packages=find_packages(exclude=['*.tests']),
    entry_points={
        'console_scripts': [
            'nete = nete.cli.main:main',
            'nete-backend = nete.backend.main:main',
        ],
    },
)
