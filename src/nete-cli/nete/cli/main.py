from nete.common.config import Config
from .nete_client import NeteClient
from .repl import Repl
import argparse
import sys
import pkg_resources

__version__ = pkg_resources.get_distribution('nete-cli').version


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default=None)
    parser.add_argument('--no-rc', action='store_true', default=False)
    parser.add_argument('-D', '--debug', action='store_true')
    parser.add_argument('-b', '--backend-url', dest='backend.url')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    return parser


defaults = {
    'debug': False,
    'api.url': 'http://localhost:8080',
}

config = Config('cli.rc', build_parser(), defaults)


def main():
    config.parse_args(sys.argv[1:])

    nete_client = NeteClient(config['backend.url'])
    repl = Repl(nete_client)
    try:
        repl.cmdloop()
    except KeyboardInterrupt:
        pass
