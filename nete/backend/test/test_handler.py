from nete.backend.handler import Handler
from nete.backend.storage.exceptions import NotFound
from aiohttp import web
import json
import pytest
import unittest.mock


class MockStorage:
    async def list(self):
        return [{'title': 'foo'}, {'title': 'bar'}]

    async def read(self, note_id):
        if note_id == 'EXISTING':
            return { 'title': 'foo' }
        else:
            raise NotFound()

    async def write(self, note):
        return {
            'id': note['id'] if 'id' in note else 'NEW-ID',
            'title': note['title']
        }


class AsyncMock(unittest.mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class TestHandler:

    storage = AsyncMock()

    @pytest.fixture
    def handler(self):
        return Handler(self.storage)

    @pytest.fixture
    def client(self, loop, test_client, handler):
        app = web.Application()
        app.router.add_get('/notes', handler.index)
        app.router.add_get('/notes/{note_id}', handler.get_note, name='note')
        app.router.add_put('/notes/{note_id}', handler.update_note)
        app.router.add_delete('/notes/{note_id}', handler.delete_note)
        app.router.add_post('/notes', handler.create_note)
        return loop.run_until_complete(test_client(app))

    async def test_index(self, client):
        self.storage.list.return_value = [{'title': 'foo'}, {'title': 'bar'}]
        response = await client.get('/notes')
        assert response.status == 200
        assert response.content_type == 'application/json'
        assert json.loads(await response.text()) == [{'title': 'foo'}, {'title': 'bar'}]

    async def test_get_note(self, client):
        self.storage.read.return_value = {'title': 'foo'}
        response = await client.get('/notes/EXISTING')
        assert response.status == 200
        assert response.content_type == 'application/json'
        assert json.loads(await response.text()) == {'title': 'foo'}

    async def test_get_note_returns_404_when_not_found(self, client):
        self.storage.read.side_effect = NotFound()
        response = await client.get('/notes/NOT-EXISTING')
        assert response.status == 404

    async def test_create_note(self, client):
        self.storage.write.return_value = {'id': 'NEW-ID', 'title': 'TITLE'}
        response = await client.post('/notes', json={'title': 'TITLE'})
        assert response.status == 201
        assert response.content_type == 'application/json'
        assert response.headers['location'] == '/notes/NEW-ID'
        assert json.loads(await response.text()) == {'id': 'NEW-ID', 'title': 'TITLE'}

    async def test_update_note(self, client):
        response = await client.put('/notes/ID', json={'title': 'TITLE'})
        self.storage.write.assert_called_with({'id': 'ID', 'title': 'TITLE'})
        assert response.status == 204
        assert await response.text() == ''

    async def test_delete_note(self, client):
        response = await client.delete('/notes/ID')
        self.storage.delete.assert_called_with('ID')
        assert response.status == 204
        assert await response.text() == ''

    async def test_delete_note_return_404_when_not_found(self, client):
        self.storage.delete.side_effect = NotFound()
        response = await client.delete('/notes/NOT-EXISTING')
        self.storage.delete.assert_called_with('NOT-EXISTING')
        assert response.status == 404
