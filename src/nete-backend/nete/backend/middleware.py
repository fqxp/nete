from .storage.exceptions import NotFound
from aiohttp import web
from marshmallow.exceptions import ValidationError
import json
import logging

logger = logging.getLogger(__name__)


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


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except ValidationError as e:
        logger.error(e)
        raise web.HTTPUnprocessableEntity(body=str(e))
    except json.decoder.JSONDecodeError as e:
        logger.error(e)
        raise web.HTTPBadRequest(body=str(e))
