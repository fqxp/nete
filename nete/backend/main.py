from .app import create_app
from .storage.filesystem import FilesystemStorage
from aiohttp import web
import argparse
import logging
try:
    import aioreloader
except ModuleNotFoundError:
    aioreloader = None

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='127.0.0.1')
    parser.add_argument('-P', '--port', type=int, default=8080)
    parser.add_argument('-S', '--socket')
    parser.add_argument('-D', '--debug', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    storage = FilesystemStorage()
    storage.open('./notes')

    app = create_app(storage)

    if args.debug and aioreloader:
        aioreloader.start(hook=storage.close)

    try:

        if args.socket:
            logger.info('starting server on socket {}'.format(args.socket))
            web.run_app(app, path=args.socket)
        else:
            logger.info('starting server on tcp://{0.host}:{0.port}'.format(args))
            web.run_app(app, host=args.host, port=args.port)
    finally:
        storage.close()
