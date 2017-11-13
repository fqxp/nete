from nete.cli.nete_client import *
import datetime
import json
import requests
import requests_mock
import pytest


class TestNeteClient:

    @pytest.fixture
    def nete_client(self):
        return NeteClient('mock://server')

    @pytest.fixture
    def server_mock(self):
        with requests_mock.mock() as m:
            yield m

    def test_list(self, nete_client, server_mock):
        server_mock.get('mock://server/notes', text=json.dumps([
            {
                'id': 'ID',
                'title': 'TITLE',
                'text': 'TEXT',
                'created_at': '2017-11-12T17:55:00',
                'updated_at': '2017-11-12T18:00:00',
            },
        ]))

        result = nete_client.list()

        assert len(result) == 1
        assert result == [{
            'id': 'ID',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': datetime.datetime(2017, 11, 12, 17, 55, 0),
            'updated_at': datetime.datetime(2017, 11, 12, 18, 00, 0),
        }]

    def test_get_note(self, nete_client, server_mock):
        server_mock.get('mock://server/notes/ID', text=json.dumps({
            'id': 'ID',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': '2017-11-12T17:55:00',
            'updated_at': '2017-11-12T18:00:00',
        }))

        result = nete_client.get_note('ID')

        assert result == {
            'id': 'ID',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': datetime.datetime(2017, 11, 12, 17, 55, 0),
            'updated_at': datetime.datetime(2017, 11, 12, 18, 00, 0),
        }

    def test_get_note_raises_NotFound_exception(self, nete_client, server_mock):
        server_mock.get(
            'mock://server/notes/NON-EXISTING-ID',
            status_code=404)

        with pytest.raises(NotFound):
            nete_client.get_note('NON-EXISTING-ID')

    def test_create_note(self, nete_client, server_mock):
        server_mock.post('mock://server/notes', text=json.dumps({
            'id': 'ID',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': '2017-11-12T17:55:00',
            'updated_at': '2017-11-12T18:00:00',
        }))

        result = nete_client.create_note({
            'title': 'TITLE',
            'text': 'TEXT',
        })

        assert server_mock.request_history[0].json() == {
            'title': 'TITLE',
            'text': 'TEXT',
        }
        assert result == {
            'id': 'ID',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': datetime.datetime(2017, 11, 12, 17, 55, 0),
            'updated_at': datetime.datetime(2017, 11, 12, 18, 00, 0),
        }

    def test_update_note(self, nete_client, server_mock):
        server_mock.put('mock://server/notes/ID', status_code=201)

        nete_client.update_note({
            'id': 'ID',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': datetime.datetime(2017, 11, 12, 17, 55, 0),
            'updated_at': datetime.datetime(2017, 11, 12, 18, 00, 0),
        })

        assert server_mock.called
        assert server_mock.request_history[0].json() == {
            'id': 'ID',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': '2017-11-12T17:55:00',
            'updated_at': '2017-11-12T18:00:00',
        }

    def test_update_note_raises_NotFound_exception(self, nete_client, server_mock):
        server_mock.put('mock://server/notes/ID', status_code=404)

        with pytest.raises(NotFound):
            nete_client.update_note({
                'id': 'ID',
                'title': 'TITLE',
                'text': 'TEXT',
                'created_at': datetime.datetime(2017, 11, 12, 17, 55, 0),
                'updated_at': datetime.datetime(2017, 11, 12, 18, 00, 0),
            })

    def test_delete_note(self, nete_client, server_mock):
        server_mock.delete('mock://server/notes/ID', status_code=201)

        nete_client.delete_note('ID')

        assert server_mock.called

    def test_delete_raises_NotFound_exception(
        self, nete_client, server_mock):
        server_mock.delete('mock://server/notes/NON-EXISTENT-ID', status_code=404)

        with pytest.raises(NotFound):
            nete_client.delete_note('NON-EXISTENT-ID')
