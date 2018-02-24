from nete.backend.handler import Handler
from nete.backend.storage.exceptions import NotFound
from nete.common.models.note import Note
from nete.backend.app import create_app
import datetime
import json
import pytest
import pytz
import unittest.mock
import uuid


class MockStorage:
    async def list(self):
        return [{'title': 'foo'}, {'title': 'bar'}]

    async def read(self, note_id):
        if note_id == 'EXISTING':
            return {'title': 'foo'}
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

    @pytest.fixture
    def storage(self):
        return AsyncMock()

    @pytest.fixture
    def handler(self, storage):
        return Handler(storage)

    @pytest.fixture
    def client(self, loop, test_client, handler, storage):
        app = create_app(storage)
        return loop.run_until_complete(test_client(app))

    async def test_index(self, client, storage):
        storage.list.return_value = [{'title': 'foo'}, {'title': 'bar'}]
        response = await client.get('/notes')
        assert response.status == 200
        assert response.content_type == 'application/json'
        assert json.loads(await response.text()) == [
            {'title': 'foo'}, {'title': 'bar'}]

    async def test_get_note(self, client, storage):
        storage.read.return_value = {'title': 'foo'}
        response = await client.get('/notes/EXISTING')
        assert response.status == 200
        assert response.content_type == 'application/json'
        assert json.loads(await response.text()) == {'title': 'foo'}

    async def test_get_note_returns_404_when_not_found(self, client, storage):
        storage.read.side_effect = NotFound()
        response = await client.get('/notes/NOT-EXISTING')
        assert response.status == 404

    @pytest.mark.freeze_time
    async def test_create_note(self, client, storage):
        id = uuid.uuid4()
        response = await client.post(
            '/notes',
            json={
                'id': str(id),
                'title': 'TITLE',
                'text': 'TEXT'
            })
        assert response.status == 201
        assert response.content_type == 'application/json'
        assert response.headers['location'] == '/notes/{}'.format(str(id))
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
        assert json.loads(await response.text()) == {
            'id': str(id),
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': now,
            'updated_at': now,
        }

    async def test_create_note_returns_422_if_data_is_invalid(self, client,
                                                              storage):
        response = await client.post(
            '/notes',
            json={
                'id': str(uuid.uuid4()),
                'title': 'TITLE',
            })
        assert response.status == 422

    async def test_create_note_returns_400_if_data_is_not_json(self, client,
                                                               storage):
        response = await client.post('/notes', data=b'{]')
        assert response.status == 400

    @pytest.mark.freeze_time
    async def test_update_note(self, client, storage):
        id = uuid.uuid4()
        storage.read.return_value = {
            'id': id, 'title': 'foo', 'text': 'hello world'}
        response = await client.put('/notes/{}'.format(str(id)),
                                    json={
                                        'id': str(id),
                                        'title': 'TITLE',
                                        'text': 'TEXT',
                                    })
        assert storage.write.call_count == 1
        assert isinstance(storage.write.call_args[0][0], Note)
        assert storage.write.call_args[0][0].__dict__ == {
            'id': id,
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow(),
            'title': 'TITLE',
            'text': 'TEXT',
        }
        assert response.status == 204
        assert await response.text() == ''

    async def test_update_note_returns_422_if_data_is_invalid(self, client,
                                                              storage):
        response = await client.put(
            '/notes/f68c7f97-611a-49de-b9cd-c1fc63300086',
            json={
                'id': 'f68c7f97-611a-49de-b9cd-c1fc63300086',
                'title': 'TITLE',
            })
        assert response.status == 422

    async def test_update_note_returns_400_if_data_is_not_json(self, client,
                                                               storage):
        response = await client.put(
            '/notes/f68c7f97-611a-49de-b9cd-c1fc63300086',
            data=b'{]')
        assert response.status == 400

    async def test_update_note_returns_404(self, client, storage):
        storage.read.side_effect = NotFound()
        id = uuid.uuid4()
        response = await client.put('/notes/{}'.format(str(id)),
                                    json={
                                        'id': str(id),
                                        'title': 'TITLE',
                                        'text': 'TEXT',
                                    })
        storage.write.assert_not_called()
        assert response.status == 404

    async def test_update_note_returns_422_if_ids_dont_match(
            self, client, storage):
        response = await client.put('/notes/{}'.format(str(uuid.uuid4())),
                                    json={
                                        'id': str(uuid.uuid4()),
                                        'title': 'TITLE',
                                        'text': 'TEXT',
                                    })
        storage.write.assert_not_called()
        assert response.status == 422

    async def test_delete_note(self, client, storage):
        response = await client.delete('/notes/ID')
        storage.delete.assert_called_with('ID')
        assert response.status == 204
        assert await response.text() == ''

    async def test_delete_note_return_404_when_not_found(
            self, client, storage):
        storage.delete.side_effect = NotFound()
        response = await client.delete('/notes/DOES-NOT-EXIST')
        storage.delete.assert_called_with('DOES-NOT-EXIST')
        assert response.status == 404
