from nete.common.xdg import XDG_CONFIG_HOME
import configparser
import logging
import os.path

logger = logging.getLogger(__name__)


class Config:

    def __init__(self, rc_filename, parser, defaults):
        self.rc_filename = rc_filename
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
        return (self.args.__dict__.get(name)
                or self.file_config.get(name)
                or self.defaults.get(name))

    def _load_config(self):
        xdg_config_filename = os.path.join(
            XDG_CONFIG_HOME,
            'nete',
            self.rc_filename)

        if self.args.no_rc:
            return {}
        elif self.args.config:
            return self._read_file(self.args.config)
        elif os.path.exists(xdg_config_filename):
            return self._read_file(xdg_config_filename)
        else:
            return {}

    def _read_file(self, filename):
        logger.info('Reading config from file {}'.format(filename))
        config_parser = configparser.ConfigParser()
        config_parser.read(filename)
        return {
            '{}.{}'.format(section, key): config_parser[section][key]
            for section in config_parser.sections()
            for key in config_parser[section]
        }
