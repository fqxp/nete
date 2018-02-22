from .storage.exceptions import NotFound
from aiohttp import web


@web.middleware
async def add_server_header(request, handler):
    response = await handler(request)
    response.headers['server'] = 'nete-backend/0.1'
    return response


@web.middleware
async def storage_exceptions_middleware(request, handler):
    try:
        return await handler(request)
    except NotFound:
        raise web.HTTPNotFound()
