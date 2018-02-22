#! /usr/bin/env python3
from setuptools import setup


setup(
    name='nete-cli',
    version='0.1',
    description='A note-taking toolset (command-line interface)',
    author='Frank Ploss',
    author_email='nete@fqxp.de',
    license='GPLv3',
    url='https://github.com/fqxp/nete-backend',
    install_requires=[
        'marshmallow',
        'python-dateutil',
        'requests',
        'requests-unixsocket',
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
        'requests-mock',
    ],
    packages=[
        'nete.cli',
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
