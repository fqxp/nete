from nete.common.xdg import XDG_CONFIG_HOME
import configparser
import logging
import os.path

logger = logging.getLogger(__name__)


class Config:

    def __init__(self, defaults):
        self.defaults = defaults
        self._file_config_attrs = {}

    def __getitem__(self, name):
        return (
            self._file_config().get(name)
            or self.defaults.get(name)
            )

    def _file_config(self):
        if self._file_config_attrs == {}:
            filename = os.environ.get(
                'NETE_CONFIG_FILE',
                os.path.join(XDG_CONFIG_HOME, 'nete', 'cli.rc')
                )
            logger.info('Reading config from file {}'.format(filename))
            config_parser = configparser.ConfigParser()
            config_parser.read(filename)
            self._file_config_attrs = {
                '{}.{}'.format(section, key): os.path.expandvars(
                    config_parser[section][key])
                for section in config_parser.sections()
                for key in config_parser[section]
            }

        return self._file_config_attrs
