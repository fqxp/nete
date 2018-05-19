from nete.backend.storage.exceptions import NotFound
from nete.backend.sync import Synchronizer
from nete.common.schemas.note_schema import NoteSchema
from aiohttp import web
import logging
import uuid

logger = logging.getLogger(__name__)

IMMUTABLE_FIELDS = ('id', 'created_at',)


class Handler:
    def __init__(self, storage, sync_url=None):
        self.storage = storage
        self.sync_url = sync_url
        self.note_schema = NoteSchema()
        self.note_index_schema = NoteSchema(exclude=['text'])

    async def index(self, request):
        notes = await self.storage.list()
        body = self.note_index_schema.dumps(notes, many=True)
        return web.Response(
            status=200,
            content_type='application/json',
            body=body)

    async def get_note(self, request):
        note_id = request.match_info['note_id']
        try:
            note = await self.storage.read(note_id)
        except NotFound:
            raise web.HTTPNotFound()

        return web.Response(
            status=200,
            content_type='application/json',
            headers={
                'etag': str(note.revision_id),
            },
            body=self.note_schema.dumps(note))

    async def create_note(self, request):
        note = self.note_schema.loads(
            await request.text())

        await self.storage.write(note)
        note_url = request.app.router['note'].url_for(note_id=str(note.id))
        return web.Response(
            status=201,
            content_type='application/json',
            headers={
                'location': str(note_url)
            },
            body=self.note_schema.dumps(note))

    async def update_note(self, request):
        if 'if-match' not in request.headers:
            raise web.HTTPBadRequest(reason='If-Match header is missing')

        note_id = uuid.UUID(request.match_info['note_id'])
        note = self.note_schema.loads(await request.text())

        if note.id != note_id:
            raise web.HTTPUnprocessableEntity(
                reason='Ids from path and from JSON body don’t match')

        old_note = await self.storage.read(note_id)

        if old_note.revision_id != uuid.UUID(request.headers.get('if-match')):
            raise web.HTTPConflict(
                reason='Edit conflict, resource has been changed '
                'since last update')

        if note.revision_id == old_note.revision_id:
            raise web.HTTPUnprocessableEntity(
                reason=('New revision id needs to be different '
                        'from old revision id'))

        changed_immutable_attributes = list(
            field
            for field in IMMUTABLE_FIELDS
            if getattr(note, field) != getattr(old_note, field))
        if any(changed_immutable_attributes):
            raise web.HTTPUnprocessableEntity(
                reason=('Tried to update immutable attributes: {!r}'
                        .format(changed_immutable_attributes)))

        await self.storage.write(note)

        return web.Response(
            status=200,
            content_type='application/json',
            body=self.note_schema.dumps(note))

    async def delete_note(self, request):
        note_id = request.match_info['note_id']
        try:
            await self.storage.delete(note_id)
            return web.Response(status=204)
        except NotFound:
            return web.HTTPNotFound()

    async def synchronize(self, request):
        if not self.sync_url:
            raise web.HTTPInternalServerError(text='No sync URL defined')

        synchronizer = Synchronizer(self.storage, self.sync_url)
        await synchronizer.synchronize()
        return web.Response(status=204)
