#! /usr/bin/env python3
from setuptools import setup


setup(
    name='nete-backend',
    version='0.1',
    description='A note-taking toolset (backend)',
    author='Frank Ploss',
    author_email='nete@fqxp.de',
    license='GPLv3',
    url='https://github.com/fqxp/nete-backend',
    install_requires=[
        'aiohttp',
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
        'aioreloader',
        'pexpect',
        'pytest',
        'pytest-aiohttp',
        'pytest-asyncio',
        'pytest-freezegun',
        'pytest-runner',
        'requests-mock',
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
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
