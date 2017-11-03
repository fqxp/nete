from .storage.exceptions import NotFound
from aiohttp import web


@web.middleware
async def storage_exceptions_middleware(request, handler):
    try:
        return await handler(request)
    except NotFound:
        raise web.HTTPNotFound()
