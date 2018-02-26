from nete.common.config import Config
from nete.common.xdg import XDG_DATA_HOME
import argparse
import os.path


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default=None)
    parser.add_argument('-D', '--debug', action='store_true')
    parser.add_argument('-H', '--api-host', dest='api.host')
    parser.add_argument('-P', '--api-port', type=int, dest='api.port')
    parser.add_argument('-S', '--api-socket', dest='api.socket')
    parser.add_argument('-s', '--storage', dest='storage.type')
    parser.add_argument('--storage-base-dir', dest='storage.base_dir')
    return parser


defaults = {
    'debug': False,
    'api.host': 'localhost',
    'api.port': 8080,
    'api.socket': None,
    'storage.type': 'filesystem',
    'storage.base_dir': os.path.join(
        XDG_DATA_HOME,
        'nete/backend/storage'),
}


config = Config('backend.rc', build_parser(), defaults)
