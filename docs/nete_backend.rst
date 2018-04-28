************
nete Backend
************

Configuration
=============
A configuration file may look like this:

.. code-block:: ini

   [api]
   socket = ./nete.socket

   [storage]
   type = filesystem
   base_dir = $HOME/notes

Location
--------

Unless you provide a ``--config`` option on the command-line, nete will
look for a configuration file in ``$XDG_CONFIG_HOME/nete/backend.rc`` (usually
that is ``~/.config/nete/backend.rc``).

You can also pass individual onfiguration options on the command-line (for example,
``--storage-base-dir ./notes``) which will take precedence over options defined in
configuration files.

Command-Line Options
---------------------

``-c FILENAME``, ``--config FILENAME``
  Read configuration from ``FILENAME`` instead of the default location
  `$XDG_CONFIG_HOME/nete/backend.rc``.

``--no-rc``
  Do not read configuration from any file.

``--api-socket FILENAME``, ``-S FILENAME``
  Unix domain socket to bind to (if given, host and port will be ignored)
  (default: `$XDG_RUNTIME_DIR/nete/socket`, which usually is
  `/run/USER-id/nette/socket`).

``--storage-base-dir``
  Directory where to store notes (default
  ``$XDG_DATA_HOME/nete/backend/storage``, usually
  ``~/.local/nete/backend/storage``).

``--sync-url URL``
  URL of remote nete instance to synchronize notes with.

``--D``, ``--debug``
  Enable debug mode.
