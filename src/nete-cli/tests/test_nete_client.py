from nete.cli.nete_client import NeteClient, NotFound
from nete.common.models import Note
import datetime
import json
import requests_mock
import pytest
import pytz
import uuid


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
                'id': 'b08cee6f-cc15-44d5-86d4-b20dfb1295b8',
                'title': 'TITLE',
                'text': 'TEXT',
                'created_at': '2017-11-12T17:55:00',
                'updated_at': '2017-11-12T18:00:00',
            },
            {
                'id': 'f75ec26c-a567-4069-86c7-17610d2a7b71',
                'title': 'ANOTHER TITLE',
                'text': 'TEXT TEXT TEXT',
                'created_at': '2018-11-13T17:55:00',
                'updated_at': '2018-11-13T18:00:00',
            },
        ]))

        result = nete_client.list()

        assert len(result) == 2
        assert result == [
            Note(
                id=uuid.UUID('b08cee6f-cc15-44d5-86d4-b20dfb1295b8'),
                title='TITLE',
                text='TEXT',
                created_at=datetime.datetime(2017, 11, 12, 17, 55, 0),
                updated_at=datetime.datetime(2017, 11, 12, 18, 00, 0),
                ),
            Note(
                id=uuid.UUID('f75ec26c-a567-4069-86c7-17610d2a7b71'),
                title='ANOTHER TITLE',
                text='TEXT TEXT TEXT',
                created_at=datetime.datetime(2018, 11, 13, 17, 55, 0),
                updated_at=datetime.datetime(2018, 11, 13, 18, 00, 0),
                )
        ]

    def test_get_note(self, nete_client, server_mock):
        server_mock.get('mock://server/notes/ID', text=json.dumps({
            'id': '1035acb6-839f-43ea-a426-7598c1ba952c',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': '2017-11-12T17:55:00',
            'updated_at': '2017-11-12T18:00:00',
        }))

        result = nete_client.get_note('ID')

        assert result == Note(
            id=uuid.UUID('1035acb6-839f-43ea-a426-7598c1ba952c'),
            title='TITLE',
            text='TEXT',
            created_at=datetime.datetime(2017, 11, 12, 17, 55, 0),
            updated_at=datetime.datetime(2017, 11, 12, 18, 00, 0),
            )

    def test_get_note_raises_NotFound_exception(self, nete_client,
                                                server_mock):
        server_mock.get(
            'mock://server/notes/NON-EXISTING-ID',
            status_code=404)

        with pytest.raises(NotFound):
            nete_client.get_note('NON-EXISTING-ID')

    @pytest.mark.freeze_time
    def test_create_note(self, nete_client, server_mock):
        server_mock.post('mock://server/notes', text=json.dumps({
            'id': 'b903730e-7553-45eb-97a0-45414cd971aa',
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
        assert result == Note(
            id=uuid.UUID('b903730e-7553-45eb-97a0-45414cd971aa'),
            title='TITLE',
            text='TEXT',
            created_at=datetime.datetime(2017, 11, 12, 17, 55, 0),
            updated_at=datetime.datetime(2017, 11, 12, 18, 00, 0),
            )

    def test_update_note(self, nete_client, server_mock):
        server_mock.put(
            'mock://server/notes/94e89308-b33e-4543-9415-be84cb1e6d38',
            status_code=201)

        note = Note(
            id=uuid.UUID('94e89308-b33e-4543-9415-be84cb1e6d38'),
            title='TITLE',
            text='TEXT',
            created_at=datetime.datetime(2017, 11, 12, 17, 55, 0,
                                         tzinfo=pytz.UTC),
            updated_at=datetime.datetime(2017, 11, 12, 18, 00, 0,
                                         tzinfo=pytz.UTC),
        )
        nete_client.update_note(note)

        assert server_mock.called
        assert server_mock.request_history[0].json() == {
            'id': '94e89308-b33e-4543-9415-be84cb1e6d38',
            'title': 'TITLE',
            'text': 'TEXT',
            'created_at': '2017-11-12T17:55:00+00:00',
            'updated_at': '2017-11-12T18:00:00+00:00',
        }

    def test_update_note_raises_NotFound_exception(self, nete_client,
                                                   server_mock):
        server_mock.put(
            'mock://server/notes/a365545f-c6cc-497a-9f89-4d38c0b29798',
            status_code=404)

        note = Note(
            id=uuid.UUID('a365545f-c6cc-497a-9f89-4d38c0b29798'),
            title='TITLE',
            text='TEXT',
            created_at=datetime.datetime(2017, 11, 12, 17, 55, 0),
            updated_at=datetime.datetime(2017, 11, 12, 18, 00, 0),
        )
        with pytest.raises(NotFound):
            nete_client.update_note(note)

    def test_delete_note(self, nete_client, server_mock):
        server_mock.delete(
            'mock://server/notes/2a22f34b-8075-4ce9-a732-c535a9b24347',
            status_code=201)

        nete_client.delete_note('2a22f34b-8075-4ce9-a732-c535a9b24347')

        assert server_mock.called

    def test_delete_raises_NotFound_exception(self, nete_client, server_mock):
        server_mock.delete('mock://server/notes/NON-EXISTENT-ID',
                           status_code=404)

        with pytest.raises(NotFound):
            nete_client.delete_note('NON-EXISTENT-ID')
