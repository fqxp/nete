from nete.util.json_util import default_serialize, note_object_hook
from aiohttp import web
import json


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
            body=json.dumps(notes, default=default_serialize).encode('utf-8'))

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
        note = await self.storage.read(note_id)
        return web.Response(
            status=200,
            content_type='application/json',
            body=json.dumps(note, default=default_serialize).encode('utf-8'))

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
        note = json.loads(await request.content.read(),
                          object_hook=note_object_hook)
        note = await self.storage.write(note)
        note_url = request.app.router['note'].url_for(note_id=note['id'])
        return web.Response(
            status=201,
            content_type='application/json',
            headers={'Location': str(note_url)},
            body=json.dumps(note, default=default_serialize).encode('utf-8'))

    async def update_note(self, request):
        """
        ---
        description: Update a note
        responses:
          "204":
            description: Successful operation.
        """
        note_id = request.match_info['note_id']
        note = json.loads(await request.content.read(),
                          object_hook=note_object_hook)
        note['id'] = note_id
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
        await self.storage.delete(note_id)
        return web.Response(status=204)
