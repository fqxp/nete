from aiohttp import web
from .handler import Handler
from .middleware import storage_exceptions_middleware
from .storage.filesystem import FilesystemStorage
import aioreloader
import argparse
import logging

DEBUG = True

logger = logging.getLogger(__name__)


def setup_routes(app, storage):
    handler = Handler(storage)
    app.router.add_get('/notes', handler.index)
    app.router.add_post('/notes', handler.create_note)
    app.router.add_get('/notes/{note_id}', handler.get_note, name='note')
    app.router.add_put('/notes/{note_id}', handler.update_note)
    app.router.add_delete('/notes/{note_id}', handler.delete_note)


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

    if DEBUG:
        aioreloader.start(hook=storage.close)

    try:
        app = web.Application(
            middlewares=[
                storage_exceptions_middleware,
            ])
        setup_routes(app, storage)

        if args.socket:
            logger.info('starting server on socket {}'.format(args.socket))
            web.run_app(app, path=args.socket)
        else:
            logger.info('starting server on tcp://{0.host}:{0.port}'.format(args))
            web.run_app(app, host=args.host, port=args.port)
    finally:
        storage.close()
