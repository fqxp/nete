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

storages = {
    'filesystem': FilesystemStorage,
}


def build_storage(config):
    kwargs = config.attributes('storage')
    storage_type = kwargs.pop('type')
    return storages[storage_type](**kwargs)


def prepare(config):
    os.makedirs(os.path.dirname(config['api.socket']), exist_ok=True)
    os.makedirs(config['storage.base_dir'], exist_ok=True)


def main():
    config.parse_args(sys.argv[1:])
    logging.basicConfig(
        filename=config['logfile'],
        filemode='w',
        level=logging.INFO)

    prepare(config)

    log_level = logging.DEBUG if config['debug'] else logging.INFO
    logging.getLogger().setLevel(log_level)

    storage = build_storage(config)
    storage.open()

    app = create_app(storage, config['sync.url'])

    if config['debug'] and aioreloader:
        aioreloader.start(hook=storage.close)

    try:
        logger.info('Starting server on socket {}'
                    .format(config['api.socket']))
        web.run_app(app, path=config['api.socket'])
        logger.info('Socket service ended.')
    except Exception as e:
        logger.error('Backend error: {}'.format(e))
        raise
    finally:
        storage.close()
        logger.info('nete-backend ended.')
