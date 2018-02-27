#! /bin/bash

if [ -z "$VIRTUAL_ENV" ] ; then
    echo "This script is meant to be run in a virtual environment."
    echo
    echo "If you want to install nete, please read the README"
    exit 1
fi

pip3 install \
    -r requirements.txt \
    -r requirements-dev.txt \
    -e src/nete-common/ \
    -e src/nete-backend/ \
    -e src/nete-cli/
