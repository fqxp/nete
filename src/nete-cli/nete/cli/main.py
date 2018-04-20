from .config import Config
from .parse_args import parse_args
from .nete_client import NeteClient
from .nete_shell import NeteShell
import sys


defaults = {
    'debug': False,
    'backend.url': 'http://localhost:8080',
}


def main():
    config = Config(defaults)
    args = parse_args(config)

    nete_client = NeteClient(config['backend.url'])
    shell = NeteShell(nete_client)

    result = shell.run(args)
    sys.exit(result)
