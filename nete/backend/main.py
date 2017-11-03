from aiohttp import web
from .handler import Handler
from .middleware import storage_exceptions_middleware
from .storage.filesystem import FilesystemStorage
import aioreloader
import logging

DEBUG = True


def setup_routes(app):
    handler = Handler(FilesystemStorage('./notes'))
    app.router.add_get('/notes', handler.index)
    app.router.add_post('/notes', handler.create_note)
    app.router.add_get('/notes/{note_id}', handler.get_note, name='note')
    app.router.add_put('/notes/{note_id}', handler.update_note)
    app.router.add_delete('/notes/{note_id}', handler.delete_note)


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = web.Application(
        middlewares=[storage_exceptions_middleware]
        )
    setup_routes(app)
    if DEBUG:
        aioreloader.start()
    web.run_app(app, host='127.0.0.1', port=8080)
