from .nete_client import NeteClient
from .repl import Repl
import argparse
import sys


def main():
    config = parse_args(sys.argv)

    nete_client = NeteClient(config.base_url)
    repl = Repl(nete_client)
    try:
        repl.cmdloop()
    except KeyboardInterrupt:
        pass


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--base-url', default=None, dest='base_url')
    return parser.parse_args()
