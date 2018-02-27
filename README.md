_pre-alpha software_

[![Build Status](https://travis-ci.org/fqxp/nete-backend.svg?branch=master)](https://travis-ci.org/fqxp/nete-backend)

# Installation

First, build the source distribution packages:

    $ ( cd src/nete-common ; ./setup.py sdist )
    $ ( cd src/nete-backend ; ./setup.py sdist )
    $ ( cd src/nete-cli ; ./setup.py sdist)

If everything went well, you can install the packages now using pip:

    $ pip install \
      src/nete-common/dist/nete-common-VERSION.tar.gz \
      src/nete-backend/dist/nete-backend-VERSION.tar.gz \
      src/nete-cli/dist/nete-cli-VERSION.tar.gz \

# Development setup

First, create a virtual environment and activate it:

    $ virtualenv venv
    $ venv/bin/activate

Then, run the `setup-development.sh` script, which will install the development
dependencies and the nete packages in development mode.

## Tests

Simply run `pytest`.
