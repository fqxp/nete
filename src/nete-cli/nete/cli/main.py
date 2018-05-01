from nete.common.xdg import XDG_RUNTIME_DIR
from .config import Config
from .parse_args import parse_args
from .nete_client import NeteClient
from .nete_shell import NeteShell
import os.path
import sys


DEFAULT_SOCKET_FILENAME = None
if XDG_RUNTIME_DIR:
    DEFAULT_SOCKET_FILENAME = 'local:{}'.format(os.path.join(XDG_RUNTIME_DIR, 'nete', 'socket'))

defaults = {
    'debug': False,
    'backend.url': DEFAULT_SOCKET_FILENAME,
}


def main():
    config = Config(defaults)
    args = parse_args(config)

    nete_client = NeteClient(config['backend.url'])
    shell = NeteShell(nete_client)

    result = shell.run(args)
    sys.exit(result)
