from .app import create_app
from .config import config
from .storage.filesystem import FilesystemStorage
from aiohttp import web
import logging
import os
import os.path
import sys
try:
    import aioreloader
except ImportError:
    aioreloader = None

logger = logging.getLogger(__name__)

STORAGES = {
    'filesystem': FilesystemStorage,
}


def main():
    config.parse_args(sys.argv[1:])

    setup_logging()
    print_config()
    create_missing_dirs()

    storage = build_storage()
    storage.open()

    app = create_app(storage, config['sync.url'])

    if config['debug'] and aioreloader:
        aioreloader.start(hook=storage.close)

    try:
        socket_path = config['api.socket']
        logger.info('Starting server on socket {}'.format(socket_path))
        web.run_app(app, path=socket_path)
    except Exception as e:
        logger.error('Backend error: {}'.format(e))
        raise
    finally:
        storage.close()
        logger.info('nete-backend ended.')


def setup_logging():
    log_level = logging.DEBUG if config['debug'] else logging.INFO
    logging.basicConfig(
        filename=config['logfile'],
        filemode='w',
        level=log_level)


def print_config():
    logger.debug('Configuration')
    for key in iter(config):
        logger.debug('  {} = {}'.format(key, config[key]))


def build_storage():
    kwargs = config.attributes('storage')
    storage_type = kwargs.pop('type')
    return STORAGES[storage_type](**kwargs)


def create_missing_dirs():
    os.makedirs(os.path.dirname(config['api.socket']), exist_ok=True)
    os.makedirs(config['storage.base_dir'], exist_ok=True)
