_beta software_

[![Build Status](https://travis-ci.org/fqxp/nete.svg?branch=master)](https://travis-ci.org/fqxp/nete)

# Installation

This repository contains three packages `nete-common`, `nete-backend` and
`nete-cli`. To build and install all of them, first read and then run the
`install.sh` script.

## Install zsh completion

Copy the file `etc/_nete.zsh` to the directory `~/.config/zsh/completion`,
and in a new shell, you should be able to use the fine command line completion.


# Development setup

First, create a virtual environment and activate it:

    $ virtualenv venv
    $ venv/bin/activate

Then, run `setup-development.sh` script, which will install the development
dependencies and the nete packages in development mode.

## Tests

Simply run `pytest`.
