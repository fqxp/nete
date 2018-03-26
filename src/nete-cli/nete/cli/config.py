from nete.common.xdg import XDG_CONFIG_HOME
import configparser
import logging
import os.path

logger = logging.getLogger(__name__)


class Config:

    def __init__(self, filename, defaults):
        self.defaults = defaults
        filename = os.environ.get(
            'NETE_CONFIG_FILE',
            os.path.join(XDG_CONFIG_HOME, 'nete', filename)
            )
        self.file_config = self._load_config(filename)

    def attributes(self, section):
        return {
            key.split('.', 1)[1]: self[key]
            for key in self.defaults.keys()
            if key.startswith(section + '.')
        }

    def __getitem__(self, name):
        return (self.file_config.get(name)
                or self.defaults.get(name))

    def _load_config(self, filename):
        logger.info('Reading config from file {}'.format(filename))
        config_parser = configparser.ConfigParser()
        config_parser.read(filename)
        return {
            '{}.{}'.format(section, key): os.path.expandvars(
                config_parser[section][key])
            for section in config_parser.sections()
            for key in config_parser[section]
        }
