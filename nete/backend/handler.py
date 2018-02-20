from nete.util.json_util import default_serialize, note_object_hook
from nete.backend.storage.exceptions import NotFound
from nete.schemas.note_schema import NoteSchema
from aiohttp import web
import json
import uuid


class Handler:
    def __init__(self, storage):
        self.storage = storage

    async def index(self, request):
        """
        ---
        description: Retrieve a list of notes.
        responses:
          "200":
            description: Successful operation.
            content:
              "application/json":
                "$ref": "#/components/schemas/NoteCollection"
        """
        notes = await self.storage.list()
        return web.Response(
            status=200,
            content_type='application/json',
            body=NoteSchema(many=True).dumps(notes))

    async def get_note(self, request):
        """
        ---
        description: Retrieve a note.
        parameters:
          name: note_id
          in: path
          required: true
        responses:
          "200":
            description: Successful operation.
            content:
              "application/json":
                "$ref": "#/components/schemas/Note"
        """
        note_id = request.match_info['note_id']
        try:
            note = await self.storage.read(note_id)
            return web.Response(
                status=200,
                content_type='application/json',
                body=NoteSchema().dumps(note))
        except NotFound:
            return web.HTTPNotFound()

    async def create_note(self, request):
        """
        ---
        description: Create a note
        produces:
        - application/json
        responses:
          "201":
            description: Successful operation.
            headers:
              Location:
                description: Path of the newly created note
            content:
              "application/json":
                "$ref": "#/components/schemas/Note"
        """
        note_schema = NoteSchema()
        note = note_schema.loads(await request.text())
        await self.storage.write(note)
        note_url = request.app.router['note'].url_for(note_id=str(note.id))
        return web.Response(
            status=201,
            content_type='application/json',
            headers={'Location': str(note_url)},
            body=note_schema.dumps(note))

    async def update_note(self, request):
        """
        ---
        description: Update a note
        responses:
          "204":
            description: Successful operation.
        """
        note_id = request.match_info['note_id']
        note_schema = NoteSchema()
        note = note_schema.loads(await request.text())
        if note.id != uuid.UUID(note_id):
            return web.HTTPUnprocessableEntity()
        # check whether item already exists
        await self.storage.read(note_id)
        await self.storage.write(note)

        return web.Response(status=204)

    async def delete_note(self, request):
        """
        ---
        description: Delete a note.
        parameters:
          name: note_id
          in: path
          required: true
        responses:
          "204":
            description: Successful operation.
        """
        note_id = request.match_info['note_id']
        try:
            await self.storage.delete(note_id)
            return web.Response(status=204)
        except NotFound:
            return web.HTTPNotFound()
