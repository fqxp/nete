from nete.backend.handler import Handler
from nete.backend.storage.exceptions import NotFound
from nete.backend.app import create_app
from nete.common.models import Note
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
        id = uuid.uuid4()
        revision_id = uuid.uuid4()
        storage.read.return_value = Note(
            id=id,
            revision_id=revision_id,
            created_at=datetime.datetime(2018, 3, 6, 17, 35, 00, tzinfo=pytz.UTC),
            updated_at=datetime.datetime(2018, 4, 7, 10, 23, 45, tzinfo=pytz.UTC),
            title='TITLE',
            text='TEXT',
            )

        response = await client.get('/notes/EXISTING')

        assert response.status == 200
        assert response.headers['etag'] == str(revision_id)
        assert response.content_type == 'application/json'
        assert json.loads(await response.text()) == {
            'id': str(id),
            'revision_id': str(revision_id),
            'created_at': '2018-03-06T17:35:00+00:00',
            'updated_at': '2018-04-07T10:23:45+00:00',
            'title': 'TITLE',
            'text': 'TEXT',
        }

    async def test_get_note_returns_404_when_not_found(self, client, storage):
        storage.read.side_effect = NotFound()

        response = await client.get('/notes/NOT-EXISTING')

        assert response.status == 404

    @pytest.mark.freeze_time
    async def test_create_note(self, client, storage):
        id = uuid.uuid4()
        revision_id = uuid.uuid4()

        response = await client.post(
            '/notes',
            json={
                'id': str(id),
                'revision_id': str(revision_id),
                'title': 'TITLE',
                'text': 'TEXT'
            })

        assert response.status == 201
        assert response.content_type == 'application/json'
        assert response.headers['location'] == '/notes/{}'.format(str(id))
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
        assert json.loads(await response.text()) == {
            'id': str(id),
            'revision_id': str(revision_id),
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': now,
            'updated_at': now,
        }

    async def test_create_note_returns_422_if_data_is_invalid(
            self, client, storage):
        response = await client.post(
            '/notes',
            json={
                'id': str(uuid.uuid4()),
                'title': 'TITLE',
            })

        assert response.status == 422

    async def test_create_note_returns_400_if_data_is_not_json(
            self, client, storage):
        response = await client.post('/notes', data=b'{]')
        assert response.status == 400

    @pytest.mark.freeze_time
    async def test_update_note(self, client, storage):
        id = uuid.uuid4()
        old_revision_id = uuid.uuid4()
        new_revision_id = uuid.uuid4()
        storage.read.return_value = Note(
            id=id,
            revision_id=old_revision_id,
            created_at=datetime.datetime(2018, 3, 6, 17, 35, 00, tzinfo=pytz.UTC),
            updated_at=datetime.datetime(2018, 4, 7, 10, 23, 45, tzinfo=pytz.UTC),
            title='OLD TITLE',
            text='OLD TEXT'
            )

        response = await client.put(
            '/notes/{}'.format(str(id)),
            json={
                'id': str(id),
                'revision_id': str(new_revision_id),
                'created_at': '2018-03-06T17:35:00+00:00',
                'updated_at': '2018-04-07T10:23:45+00:00',
                'title': 'NEW TITLE',
                'text': 'NEW TEXT',
            },
            headers={
                'if-match': str(old_revision_id),
            })

        assert response.status == 200
        assert storage.write.call_count == 1
        assert storage.write.call_args[0][0].id == id
        updated_note = json.loads(await response.text())
        assert updated_note == {
            'id': str(id),
            'revision_id': str(new_revision_id),
            'created_at': '2018-03-06T17:35:00+00:00',
            'updated_at': '2018-04-07T10:23:45+00:00',
            'title': 'NEW TITLE',
            'text': 'NEW TEXT',
        }

    async def test_update_note_returns_400_if_data_is_not_json(
            self, client, storage):
        old_revision_id = uuid.uuid4()
        storage.read.return_value = Note(
            id=id,
            revision_id=old_revision_id,
            created_at=datetime.datetime(2018, 3, 6, 17, 35, 00, tzinfo=pytz.UTC),
            updated_at=datetime.datetime(2018, 4, 7, 10, 23, 45, tzinfo=pytz.UTC),
            title='OLD TITLE',
            text='OLD TEXT'
            )

        response = await client.put(
            '/notes/f68c7f97-611a-49de-b9cd-c1fc63300086',
            headers={
                'if-match': str(old_revision_id),
            },
            data=b'{]')
        assert response.status == 400

    async def test_update_note_returns_404_if_not_found(self, client, storage):
        storage.read.side_effect = NotFound()
        id = uuid.uuid4()
        response = await client.put(
            '/notes/{}'.format(str(id)),
            headers={
                'if-match': '6268f211-b9f3-471c-a076-728809f38e96',
            },
            json={
                'id': str(id),
                'revision_id': str(uuid.uuid4()),
                'title': 'TITLE',
                'text': 'TEXT',
            })
        storage.write.assert_not_called()
        assert response.status == 404

    async def test_update_note_returns_422_if_ids_from_path_and_data_dont_match(
            self, client, storage):
        response = await client.put(
            '/notes/bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            json={
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                'revision_id': str(uuid.uuid4()),
                'created_at': '2018-03-06T17:35:00+00:00',
                'updated_at': '2018-04-07T10:23:45+00:00',
                'title': 'NEW TITLE',
                'text': 'NEW TEXT',
            },
            headers={
                'if-match': str(uuid.uuid4()),
            })

        assert response.status == 422

    async def test_update_note_returns_422_if_data_is_invalid(
            self, client, storage):
        old_revision_id = uuid.uuid4()
        storage.read.return_value = Note(
            id=id,
            revision_id=old_revision_id,
            created_at=datetime.datetime(2018, 3, 6, 17, 35, 00, tzinfo=pytz.UTC),
            updated_at=datetime.datetime(2018, 4, 7, 10, 23, 45, tzinfo=pytz.UTC),
            title='OLD TITLE',
            text='OLD TEXT'
            )

        response = await client.put(
            '/notes/f68c7f97-611a-49de-b9cd-c1fc63300086',
            headers={
                'if-match': str(old_revision_id),
            },
            json={
                'id': 'f68c7f97-611a-49de-b9cd-c1fc63300086',
                'title': 'TITLE',
            })

        assert response.status == 422

    async def test_update_note_returns_422_when_trying_to_change_immutable_fields(
            self, client, storage):
        id = uuid.uuid4()
        old_revision_id = uuid.uuid4()
        new_revision_id = uuid.uuid4()
        storage.read.return_value = Note(
            id=id,
            revision_id=old_revision_id,
            created_at=datetime.datetime(2018, 3, 6, 17, 35, 00, tzinfo=pytz.UTC),
            updated_at=datetime.datetime(2018, 4, 7, 10, 23, 45, tzinfo=pytz.UTC),
            title='OLD TITLE',
            text='OLD TEXT'
            )

        # trying to update created_at field
        response = await client.put(
            '/notes/{}'.format(str(id)),
            json={
                'id': str(id),
                'revision_id': str(new_revision_id),
                'created_at': '2017-03-06T17:35:00+00:00',
                'updated_at': '2018-04-07T10:23:45+00:00',
                'title': 'TITLE',
                'text': 'TEXT',
            },
            headers={
                'if-match': str(old_revision_id),
            })

        assert response.status == 422

    async def test_update_note_returns_400_if_if_match_header_is_missing(
            self, client, storage):
        response = await client.put(
            '/notes/85d63b94-742c-4482-ac37-cf15881120e0',
            json={})

        assert response.status == 400

    async def test_update_note_returns_409_if_revision_does_not_match(
            self, client, storage):
        id = uuid.uuid4()
        old_revision_id = uuid.uuid4()
        new_revision_id = uuid.uuid4()
        storage.read.return_value = Note(
            id=id,
            revision_id=old_revision_id,
            title='ANOTHER TITLE',
            text='ANOTHER TEXT',
            )

        response = await client.put(
            '/notes/{}'.format(id),
            json={
                'id': str(id),
                'revision_id': str(new_revision_id),
                'created_at': '2018-03-06T17:35:00+00:00',
                'updated_at': '2018-04-07T10:23:45+00:00',
                'title': 'NEW TITLE',
                'text': 'NEW TEXT',
            },
            headers={
                'if-match': str(uuid.uuid4()),
            })

        storage.write.assert_not_called()
        assert response.status == 409

    async def test_update_note_returns_422_if_revision_has_not_been_updated(
            self, client, storage):
        id = uuid.uuid4()
        old_revision_id = uuid.uuid4()
        storage.read.return_value = Note(
            id=id,
            revision_id=old_revision_id,
            created_at=datetime.datetime(2018, 3, 6, 17, 35, 00, tzinfo=pytz.UTC),
            updated_at=datetime.datetime(2018, 4, 7, 10, 23, 45, tzinfo=pytz.UTC),
            title='ANOTHER TITLE',
            text='ANOTHER TEXT',
            )

        response = await client.put(
            '/notes/{}'.format(str(id)),
            json={
                'id': str(id),
                'revision_id': str(old_revision_id),
                'created_at': '2018-03-06T17:35:00+00:00',
                'updated_at': '2018-04-07T10:23:45+00:00',
                'title': 'NEW TITLE',
                'text': 'NEW TEXT',
            },
            headers={
                'if-match': str(old_revision_id),
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
