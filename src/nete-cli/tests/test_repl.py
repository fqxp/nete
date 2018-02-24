from nete.common.models import Note
from unittest.mock import MagicMock
import datetime
import nete.cli.repl
import pytest
import pytz
import uuid


@pytest.fixture
def nete_client():
    return MagicMock()


@pytest.fixture
def repl(nete_client):
    return nete.cli.repl.Repl(nete_client)


def test_ls_returns_list_of_notes(repl, nete_client, capsys):
    nete_client.list.return_value = [
        Note(id=uuid.UUID('02665506-be9c-4c72-8c93-da8625061168'),
             title='TITLE 1', text='TEXT 1'),
        Note(id=uuid.UUID('9af112f7-9094-4166-aaa5-f1646670d428'),
             title='TITLE 2', text='TEXT 2'),
    ]

    repl.onecmd('ls')

    captured = capsys.readouterr()
    assert (captured.out ==
            '02665506-be9c-4c72-8c93-da8625061168   TITLE 1\n'
            '9af112f7-9094-4166-aaa5-f1646670d428   TITLE 2\n')


def test_cat_outputs_note(repl, nete_client, capsys):
    nete_client.get_note.return_value = Note(
        id=uuid.UUID('02665506-be9c-4c72-8c93-da8625061168'),
        title='TITLE 1', text='TEXT 1',
        created_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
        updated_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
        )

    repl.onecmd('cat 02665506-be9c-4c72-8c93-da8625061168')

    nete_client.get_note.assert_called_once_with(
        '02665506-be9c-4c72-8c93-da8625061168')
    captured = capsys.readouterr()
    assert (captured.out ==
            'Title: TITLE 1\n'
            'Id: 02665506-be9c-4c72-8c93-da8625061168\n'
            'Created-At: 2017-01-01 12:00:00+00:00\n'
            'Updated-At: 2017-01-01 12:00:00+00:00\n'
            '\n'
            'TEXT 1\n')


@pytest.mark.freeze_time
def test_new_lets_user_edit_note_and_saves_it(repl, nete_client, capsys):
    note_after_editing = Note(id=None, title='TITLE 1', text='TEXT 1',
                              created_at=None, updated_at=None)

    nete.cli.repl.edit_note = MagicMock(return_value=note_after_editing)
    nete_client.create_note.return_value = Note(
        id=uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'),
        title='TITLE 1',
        text='TEXT 1',
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
        )
    nete.cli.repl.input = MagicMock(return_value='NOTE NAME')

    repl.onecmd('new')

    nete_client.create_note.called_with(note_after_editing)
    captured = capsys.readouterr()
    assert (captured.out ==
            'Created note with id 80463678-3882-458e-a12c-eb78059f3a52\n')


@pytest.mark.freeze_time
def test_edit_lets_user_edit_note_and_saves_it(repl, nete_client):
    note = Note(
        id=uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'),
        title='TITLE',
        text='TEXT',
        created_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
        updated_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC))
    note_after_editing = Note(
        id=uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'),
        title='UPDATED TITLE',
        text='UPDATED TEXT',
        created_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
        updated_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC))
    nete_client.get_note.return_value = note
    nete.cli.repl.edit_note = MagicMock(return_value=note_after_editing)

    repl.onecmd('edit 80463678-3882-458e-a12c-eb78059f3a52')

    nete_client.get_note.assert_called_once_with(
        uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'))
    nete.cli.repl.edit_note.assert_called_once_with(note)
    nete_client.update_note.assert_called_once_with(note_after_editing)


def test_rm_deletes_note(repl, nete_client):
    repl.onecmd('rm 80463678-3882-458e-a12c-eb78059f3a52')

    nete_client.delete_note.assert_called_once_with(
        uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'))
