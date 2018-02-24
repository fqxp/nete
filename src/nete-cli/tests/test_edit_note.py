from nete.cli.edit_note import (
    edit_note, ParseError, render_editable_note, parse_editable_note)
from nete.cli.test_utils.editor import Editor
from nete.common.models import Note
import datetime
import os
import pytest
import uuid


@pytest.fixture
def note():
    return Note(
        id=uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'),
        title='TITLE',
        text='TEXT',
        created_at=datetime.datetime(2017, 1, 1, 12, 30, 45),
        updated_at=datetime.datetime(2017, 1, 2, 12, 30, 45),
    )


@pytest.fixture
def editor():
    with Editor() as editor:
        os.environ.update(editor.env())
        yield editor


def test_edit_note_returns_parsed_note(note, editor):
    editor.set_content(
        'Title: NEW TITLE\n'
        'Id: CHANGED ID\n'
        '\n'
        'NEW TEXT'
    )

    result = edit_note(note)

    assert result == Note(
        id=uuid.UUID('80463678-3882-458e-a12c-eb78059f3a52'),
        title='NEW TITLE',
        text='NEW TEXT',
        created_at=datetime.datetime(2017, 1, 1, 12, 30, 45),
        updated_at=datetime.datetime(2017, 1, 2, 12, 30, 45),
    )


def test_parse_editable_note_returns_parsed_note():
    editable_note = (
        'Title: NEW TITLE\n'
        'Id: CHANGED ID\n'
        'Created-At: <not set>\n'
        'Updated-At: <not set>\n'
        '# some comment\n'
        '\n'
        'NEW TEXT'
    )

    result = parse_editable_note(editable_note)

    assert result == {
        'title': 'NEW TITLE',
        'text': 'NEW TEXT',
    }


def test_parse_editable_note_raises_exception_if_format_not_ok():
    with pytest.raises(ParseError):
        parse_editable_note('SOME TEXT')

    with pytest.raises(ParseError):
        parse_editable_note('')


def test_parse_editable_note_raises_exception_for_unknown_headers():
    editable_note = (
        'Title: TITLE\n'
        'Invalid-Header: some value\n'
        '\n'
        'TEXT'
    )
    with pytest.raises(ParseError):
        parse_editable_note(editable_note)


def test_render_editable_note_renders_note_as_rfc_822_style_text(note):
    result = render_editable_note(note)

    assert result == (
        'Title: TITLE\n'
        'Id: 80463678-3882-458e-a12c-eb78059f3a52\n'
        'Created-At: 2017-01-01 12:30:45\n'
        'Updated-At: 2017-01-02 12:30:45\n'
        '\n'
        'TEXT'
    )


def test_render_editable_note_includes_comments_in_editor_text(note):
    result = render_editable_note(note, 'comment 1\ncomment 2')

    assert result == (
        'Title: TITLE\n'
        'Id: 80463678-3882-458e-a12c-eb78059f3a52\n'
        'Created-At: 2017-01-01 12:30:45\n'
        'Updated-At: 2017-01-02 12:30:45\n'
        '# comment 1\n'
        '# comment 2\n'
        '\n'
        'TEXT'
    )
