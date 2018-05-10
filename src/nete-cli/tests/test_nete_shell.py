from nete.cli.nete_client import NotFound
from nete.common.models import Note
from unittest.mock import MagicMock
import datetime
import nete.cli.nete_shell
import pytest
import pytz
import uuid


@pytest.fixture
def nete_client():
    return MagicMock()


@pytest.fixture
def nete_shell(nete_client):
    return nete.cli.nete_shell.NeteShell(nete_client, config={})


def test_ls_returns_list_of_notes(nete_shell, nete_client, capsys):
    nete_client.list.return_value = [
        Note(id=uuid.UUID('02665506-be9c-4c72-8c93-da8625061168'),
             title='TITLE 1', text='TEXT 1'),
        Note(id=uuid.UUID('9af112f7-9094-4166-aaa5-f1646670d428'),
             title='TITLE 2', text='TEXT 2'),
    ]

    result = nete_shell.ls()

    captured = capsys.readouterr()
    assert (captured.out ==
            '02665506-be9c-4c72-8c93-da8625061168   TITLE 1\n'
            '9af112f7-9094-4166-aaa5-f1646670d428   TITLE 2\n')
    assert result == 0


def test_cat_outputs_note(nete_shell, nete_client, capsys):
    nete_client.get_note.return_value = Note(
        id=uuid.UUID('02665506-be9c-4c72-8c93-da8625061168'),
        title='TITLE 1', text='TEXT 1',
        created_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
        updated_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
        )

    result = nete_shell.cat(['02665506-be9c-4c72-8c93-da8625061168'])

    nete_client.get_note.assert_called_once_with(
        uuid.UUID('02665506-be9c-4c72-8c93-da8625061168'))
    captured = capsys.readouterr()
    assert (captured.out ==
            'Title: TITLE 1\n'
            'Id: 02665506-be9c-4c72-8c93-da8625061168\n'
            'Created-At: 2017-01-01 12:00:00+00:00\n'
            'Updated-At: 2017-01-01 12:00:00+00:00\n'
            '\n'
            'TEXT 1\n')
    assert result == 0


def test_cat_prints_error_if_not_found(nete_shell, nete_client, capsys):
    nete_client.get_note.side_effect = NotFound('ID')

    result = nete_shell.cat(['02665506-be9c-4c72-8c93-da8625061168'])

    captured = capsys.readouterr()
    assert ('not found' in captured.out.lower())
    assert result == 1


@pytest.mark.freeze_time
def test_new_lets_user_edit_note_and_saves_it(nete_shell, nete_client, capsys):
    note_after_editing = Note(id=None, title='TITLE 1', text='TEXT 1',
                              created_at=None, updated_at=None)

    nete.cli.nete_shell.edit_note = MagicMock(return_value=note_after_editing)
    nete_client.create_note.return_value = Note(
        id=uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'),
        title='TITLE 1',
        text='TEXT 1',
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
        )

    result = nete_shell.new('NOTE NAME')

    nete_client.create_note.called_with(note_after_editing)
    captured = capsys.readouterr()
    assert (captured.out ==
            'Created note with id 80463678-3882-458e-a12c-eb78059f3a52\n')
    assert result == 0


@pytest.mark.freeze_time
def test_edit_lets_user_edit_note_and_saves_it(nete_shell, nete_client):
    note = Note(
        id=uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'),
        revision_id=uuid.UUID('10463678-3882-458e-a12c-eb78059f3a52'),
        title='TITLE',
        text='TEXT',
        created_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
        updated_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC))
    note_after_editing = Note(
        id=uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'),
        revision_id=uuid.UUID('deadbeef-dead-dead-dead-deaddeaddead'),
        title='UPDATED TITLE',
        text='UPDATED TEXT',
        created_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
        updated_at=datetime.datetime(2017, 1, 1, 12, 0, 0, tzinfo=pytz.UTC))
    nete_client.get_note.return_value = note
    nete.cli.nete_shell.edit_note = MagicMock(return_value=note_after_editing)

    result = nete_shell.edit('80463678-3882-458e-a12c-eb78059f3a52')

    nete_client.get_note.assert_called_once_with(
        uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'))
    nete.cli.nete_shell.edit_note.assert_called_once_with(note)
    nete_client.update_note.assert_called_once_with(
        note_after_editing,
        old_revision_id=uuid.UUID('10463678-3882-458e-a12c-eb78059f3a52'))
    assert result == 0


def test_edit_prints_not_found_if_note_doesnt_exist(
        nete_shell, nete_client, capsys):
    nete_client.get_note.side_effect = NotFound('ID')

    result = nete_shell.edit('80463678-3882-458e-a12c-eb78059f3a52')

    captured = capsys.readouterr()
    assert ('not found' in captured.out.lower())
    assert result == 1


def test_rm_deletes_note(nete_shell, nete_client):
    result = nete_shell.rm(['80463678-3882-458e-a12c-eb78059f3a52'])

    nete_client.delete_note.assert_called_once_with(
        uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'))
    assert result == 0


def test_rm_prints_not_found_if_note_doesnt_exist(
        nete_shell, nete_client, capsys):
    nete_client.delete_note.side_effect = NotFound('ID')

    result = nete_shell.rm(['80463678-3882-458e-a12c-eb78059f3a52'])

    captured = capsys.readouterr()
    assert ('not found' in captured.out.lower())
    assert result == 1
