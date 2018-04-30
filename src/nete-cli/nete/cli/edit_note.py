from nete.common.models import Note
import os
import subprocess
import tempfile


class ParseError(Exception):
    pass


class EditorException(Exception):
    pass


HEADER_MAPPINGS = (
    {'attr': 'title', 'header': 'Title'},
    {'attr': 'id', 'header': 'Id', 'default': '<not set>'},
    {'attr': 'created_at', 'header': 'Created-At', 'default': '<not set>'},
    {'attr': 'updated_at', 'header': 'Updated-At', 'default': '<not set>'},
)


def edit_note(note, message=None):
    with tempfile.NamedTemporaryFile(suffix='.nete') as fp:
        fp.write(render_editable_note(note, message).encode('utf-8'))
        fp.flush()
        result = subprocess.run(
            '{} {}'.format(os.environ.get('EDITOR'), fp.name),
            shell=True)

        if result.returncode > 0:
            raise EditorException(
                'Editor returned non-zero result.'
                'Not changing note.')

        fp.seek(0)
        data = fp.read().decode('utf-8')
        return Note(**{**note.__dict__, **parse_editable_note(data)})


def render_editable_note(note, message=None):
    headers = ''.join(
        "{}: {}\n".format(
            mapping['header'],
            note.__dict__.get(mapping['attr'], mapping.get('default')))
        for mapping in HEADER_MAPPINGS)
    messages = (''.join('# {}\n'.format(line)
                        for line in message.split('\n'))
                if message else '')

    return '{}{}\n{}'.format(headers, messages, note.text)


def parse_editable_note(formatted_note):
    header_data, _, text = formatted_note.partition('\n\n')

    try:
        headers = dict(
            line.split(': ', 1)
            for line in header_data.splitlines()
            if not line.startswith('#'))
    except ValueError:
        raise ParseError('Header formatting is not right.')

    if headers == {}:
        raise ParseError('No headers found.')

    allowed_headers = list(mapping['header'] for mapping in HEADER_MAPPINGS)
    invalid_headers = ', '.join(key
                                for key in headers.keys()
                                if key not in allowed_headers)
    if invalid_headers:
        raise ParseError('Header(s) {} are unknown.'
                         .format(invalid_headers))

    return {
        'title': headers.get('Title'),
        'text': text,
    }
