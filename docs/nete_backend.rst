************
nete Backend
************

Configuration
=============
A configuration file may look like this:

.. code-block:: ini

   [api]
   host = localhost
   port = 8080

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
  Read configuration from ``FILENAME`` instead of default location.

``--no-rc``
  Do not read configuration from any file.

``-H HOSTNAME``, ``--api-host HOSTNAME``
  Hostname to whose IP address to bind the HTTP API port to (default:
  ``localhost``).

``-P PORT``, ``--api-port PORT``
  Port to bind to (default: ``8080``).

``-S FILENAME``, ``--api-socket FILENAME``
  Unix domain socket to bind to (if given, host and port will be ignored)
  (default: *not set*).

``--storage-base-dir``
  Directory where to store notes (default
  ``$XDG_DATA_HOME/nete/backend/storage``, usually
  ``~/.local/nete/backend/storage``).

``--D``, ``--debug``
  Enable debug mode.
