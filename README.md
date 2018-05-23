_beta software_

[![Build Status](https://travis-ci.org/fqxp/nete.svg?branch=master)](https://travis-ci.org/fqxp/nete)
[![codecov](https://codecov.io/gh/fqxp/nete/branch/master/graph/badge.svg)](https://codecov.io/gh/fqxp/nete)
[![Maintainability](https://api.codeclimate.com/v1/badges/250379bc91e125e71dcc/maintainability)](https://codeclimate.com/github/fqxp/nete/maintainability)
[![Requirements Status](https://requires.io/github/fqxp/nete/requirements.svg?branch=master)](https://requires.io/github/fqxp/nete/requirements/?branch=master)

# Installation

## Prerequisites

* Python >=3.5
* libsodium
* libkrb5-dev

## `install.sh`

This repository contains three packages `nete-common`, `nete-backend` and
`nete-cli`. To build and install all of them, first read and then run the
`install.sh` script.

## Install zsh Completion

Copy the file `etc/_nete.zsh` to the directory `~/.config/zsh/completion`,
and in a new shell, you should be able to use the fine command line completion.

# Usage

## Run the Backend

You can start the backend by running the command

    $ nete-backend

without any options or configuration file. If you want to configure a different
socket path or a sync URL, you need a configuration file (see below).

For available options, use

    $ nete-backend --help

### systemd Configuration

You probably want to start nete-backend automatically when you log in. For this,
put a systemd service file with the following content into
`~/.config/systemd/user/nete-backend.service` (replace `PATH_TO_INSTALL_BIN` by
the directory the `nete-backend` command is installed in):

    [Unit]
    Description=nete Backend Service

    [Service]
    ExecStart=PATH_TO_INSTALL_BIN/nete-backend

    [Install]
    WantedBy=default.target

Then enable the service:

    $ systemctl --user daemon-reload
    $ systemctl --user enable nete-backend.service
    $ systemctl --user start nete-backend.service

## Command Line Usage

Run

    $ nete --help

for a quick summary of available commands. For example, you can create, list and
edit notes likes this:

    $ nete new "My new note"
    ... edit with $EDITOR ...
    $ nete ls
    f05046bb-5ea3-496a-880a-3069df86a97e   My new note
    $ nete edit f05046bb-5ea3-496a-880a-3069df86a97e
    ... edit ...

## Optional: Configure Backend

You can use nete without any configuration file at all. But if you want to use
synchronization or if you have special requirements, you can create one.

nete will read either no or one configuration file. It will look for it in

* the location specified by the `--config` option or
* `$XDG_CONFIG_HOME/nete/backend.rc` (usually, this is
  `~/.config/nete/backend.rc`)

These are the options you can configure (and the defaults used):

    [api]
    socket = $XDG_RUNTIME_DIR/nete/socket
    [storage]
    type = filesystem
    base_dir = $XDG_DATA_HOME/nete/backend/storage
    [sync]
    url =         # no default; see below

## Optional: Configure Command Line Interface

The CLI configuration is not necessary either unless you want to deviate from
the default configuration. `nete` looks for it in either `$NETE_CONFIG_FILE`
(meaning you can override it by setting the environment variable
`NETE_CONFIG_FILE`) or in `$XDG_CONFIG_HOME/nete/cli.rc`.

Currently, there is only one option you can set in the configuration file:

    [backend]
    url = local:$XDG_RUNTIME_DIR/nete/socket

The URL can be either a Unix Domain Socket path (denoted by a `local:` prefix)
or an HTTP URL (denoted by either `http:` or `https:`).

## Synchronization

nete is able to synchronize with a remote server via SSH. For this to work, you
need only little setup.

### Prerequisites

You need to install nete and nete-backend with the same versions as locally
on the remote side. Make sure nete-backend is running when you log in, e. g. by
starting it through systemd (see above).

It works if the following command prints the path of the Unix Domain Socket
when executed on the local side:

    $ ssh SYNCHOST nete socket
    /run/user/1234/nete/socket

Use an SSH agent (like ssh-agent or gpg-agent), otherwise nete-backend won’t be
able to authenticate.

### Configuration

Tell your local nete-backend which host you want to synchronize with by adding
sync URL parameter to your configuration (see above):

    [sync]
    url = http+ssh://USERNAME@SYNCHOST[:PORT]

### Run Synchronization

You should now be all set and can run:

    $ nete sync

Take a look at the logs of the local nete backend to see what’s happening.

# Development Setup

First, create a virtual environment and activate it:

    $ virtualenv venv
    $ venv/bin/activate

Then, run `setup-development.sh` script, which will install the development
dependencies and the nete packages in development mode.

## Tests

Simply run `pytest`.
