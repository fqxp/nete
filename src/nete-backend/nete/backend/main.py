from .app import create_app
from .config import config
from .storage.filesystem import FilesystemStorage
from aiohttp import web
import logging
import sys
try:
    import aioreloader
except ModuleNotFoundError:
    aioreloader = None

logger = logging.getLogger(__name__)

storages = {
    'filesystem': FilesystemStorage,
}


def build_storage(config):
    kwargs = config.attributes('storage')
    storage_type = kwargs.pop('type')
    return storages[storage_type](**kwargs)


def main():
    config.parse_args(sys.argv[1:])
    logging.basicConfig(
        filename=config['logfile'],
        filemode='w',
        level=logging.INFO)

    log_level = logging.DEBUG if config['debug'] else logging.INFO
    logging.getLogger().setLevel(log_level)

    storage = build_storage(config)
    storage.open()

    app = create_app(storage)

    if config['debug'] and aioreloader:
        aioreloader.start(hook=storage.close)

    try:
        if config['api.socket']:
            logger.info('Starting server on socket {}'
                        .format(config['api.socket']))
            web.run_app(app, path=config['api.socket'])
        else:
            logger.info('Starting server on tcp://{}:{}'.format(
                config['api.host'], config['api.port']))
            web.run_app(app, host=config['api.host'], port=config['api.port'])
    finally:
        storage.close()
