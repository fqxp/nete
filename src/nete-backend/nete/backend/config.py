from nete.common.nete_url import NeteUrl
from nete.common.xdg import XDG_CONFIG_HOME, XDG_DATA_HOME, XDG_RUNTIME_DIR
import argparse
import configparser
import logging
import os.path
import pkg_resources

logger = logging.getLogger(__name__)

__version__ = pkg_resources.get_distribution('nete-backend').version

DEFAULT_CONFIG_FILENAME = os.path.join(
    XDG_CONFIG_HOME,
    'nete',
    'backend.rc')

DEFAULT_SOCKET_FILENAME = None
if XDG_RUNTIME_DIR:
    DEFAULT_SOCKET_FILENAME = os.path.join(XDG_RUNTIME_DIR, 'nete', 'socket')


defaults = {
    'debug': False,
    'api.socket': DEFAULT_SOCKET_FILENAME,
    'logfile': '/dev/stdout',
    'storage.type': 'filesystem',
    'storage.base_dir': os.path.join(
        XDG_DATA_HOME, 'nete', 'backend', 'storage')
        if XDG_DATA_HOME else None,
    'sync.url': None,
}

types = {
    'sync.url': NeteUrl.from_string,
}

class Config:

    def __init__(self, parser, defaults):
        self.parser = parser
        self.defaults = defaults

    def parse_args(self, command_line_args):
        self.args = self.parser.parse_args(command_line_args)
        self.file_config = self._load_config()

    def attributes(self, section):
        return {
            key.split('.', 1)[1]: self[key]
            for key in self.defaults.keys()
            if key.startswith(section + '.')
        }

    def __getitem__(self, name):
        value = (self.args.__dict__.get(name)
                or self.file_config.get(name)
                or self.defaults.get(name))
        value_type = types.get(name, str)
        return value_type(value) if value is not None else None

    def __iter__(self):
        return iter(set([
            *self.args.__dict__.keys(),
            *self.file_config.keys(),
            *self.defaults.keys()]))

    def _load_config(self):

        if self.args.no_rc:
            return {}
        elif self.args.config:
            return self._read_file(self.args.config)
        elif os.path.exists(DEFAULT_CONFIG_FILENAME):
            return self._read_file(DEFAULT_CONFIG_FILENAME)
        else:
            logger.info('Didn’t find any config file, continuing with default config')
            return {}

    def _read_file(self, filename):
        logger.info('Reading config from file {}'.format(filename))
        config_parser = configparser.ConfigParser()
        config_parser.read(filename)
        return {
            '{}.{}'.format(section, key): os.path.expandvars(
                config_parser[section][key])
            for section in config_parser.sections()
            for key in config_parser[section]
        }


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        default=None,
        help='config file [{}]'.format(DEFAULT_CONFIG_FILENAME))
    parser.add_argument(
        '--no-rc',
        action='store_true',
        default=False,
        help='don’t load any config file at all')
    parser.add_argument(
        '-D', '--debug',
        action='store_true',
        help='enable debug logging')
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=__version__)
    return parser


config = Config(build_parser(), defaults)
