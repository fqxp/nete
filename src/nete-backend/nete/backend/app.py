from aiohttp import web
from .handler import Handler
from .middleware import (add_server_header, storage_exceptions_middleware,
                         error_middleware)


def create_app(storage, sync_url=None):
    app = web.Application(
        middlewares=[
            add_server_header,
            storage_exceptions_middleware,
            error_middleware,
        ])
    handler = Handler(storage, sync_url)
    setup_routes(app, handler)

    return app


def setup_routes(app, handler):
    app.router.add_get('/notes', handler.index)
    app.router.add_post('/notes', handler.create_note)
    app.router.add_get('/notes/sync', handler.synchronize)
    app.router.add_get('/notes/{note_id}', handler.get_note, name='note')
    app.router.add_put('/notes/{note_id}', handler.update_note)
    app.router.add_delete('/notes/{note_id}', handler.delete_note)
