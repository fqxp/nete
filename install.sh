#! /bin/bash

set -e

for pkg_base in src/nete-common src/nete-backend src/nete-cli ; do
    (
        cd "$pkg_base" || exit 1
        rm dist/*
        ./setup.py sdist
        /usr/bin/pip install --user --upgrade dist/*.tar.gz
    )
done
