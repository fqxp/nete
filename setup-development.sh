#! /bin/bash

pip3 install \
    -r requirements.txt \
    -r requirements-dev.txt \
    -e src/nete-common/ \
    -e src/nete-backend/ \
    -e src/nete-cli/
