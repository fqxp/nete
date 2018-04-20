import configparser
import contextlib
import tempfile
import logging

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def config_fixture(config_dict):
    with tempfile.NamedTemporaryFile(mode='w') as config_file:
        config = configparser.ConfigParser()
        config.update(config_dict)
        config.write(config_file)
        config_file.flush()

        yield config_file.name
