import argparse
import configparser
import logging
import os.path

logger = logging.getLogger(__name__)


class Config:

    defaults = {
        'debug': False,
        'api.host': 'localhost',
        'api.port': 8080,
        'api.socket': None,
        'storage.type': 'filesystem',
        'storage.base_dir': None,
    }

    def __init__(self, args):
        self.args = self.parse_args(args)
        xdg_config_filename = os.path.join(
            os.environ.get(
                'XDG_CONFIG_HOME',
                os.path.expanduser('~/.config')),
            'nete/backend.rc')

        if self.args.config:
            self.file_config = self.read_file(self.args.config)
        elif os.path.exists(xdg_config_filename):
            self.file_config = self.read_file(xdg_config_filename)
        elif os.path.exists('/etc/nete/backend.rc'):
            self.file_config = self.read_file('/etc/nete/backend.rc')
        else:
            self.file_config = {}

    def parse_args(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', default=None)
        parser.add_argument('-D', '--debug', action='store_true')
        parser.add_argument('-H', '--api-host', dest='api.host')
        parser.add_argument('-P', '--api-port', type=int, dest='api.port')
        parser.add_argument('-S', '--api-socket', dest='api.socket')
        parser.add_argument('-s', '--storage', dest='storage.type')
        parser.add_argument('--storage-base-dir', dest='storage.base_dir')
        return parser.parse_args()

    def read_file(self, filename):
        logger.info('Reading config from file {}'.format(filename))
        config_parser = configparser.ConfigParser()
        config_parser.read(filename)
        return {
            '{}.{}'.format(section, key): config_parser[section][key]
            for section in config_parser.sections()
            for key in config_parser[section]
        }

    def attributes(self, section):
        return {
            key.split('.', 1)[1]: self[key]
            for key in self.defaults.keys()
            if key.startswith(section + '.')
        }

    def __getitem__(self, name):
        return (self.args.__dict__.get(name)
                or self.file_config.get(name)
                or self.defaults.get(name))
