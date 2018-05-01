#! /bin/bash

set -e

declare -a pkgs=(src/nete-common src/nete-backend src/nete-cli)

for pkg_base in ${pkgs[@]} ; do
    (
        cd "$pkg_base" || exit 1
        rm -f dist/*
        ./setup.py sdist
    )
done

pip3 install --user --upgrade -r requirements.txt ${pkgs[@]/%//dist/*.tar.gz}
