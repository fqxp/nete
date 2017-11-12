from .nete_client import NotFound
import cmd
import os
import re
import subprocess
import tempfile


class Repl(cmd.Cmd):

    def __init__(self, nete_client):
        super().__init__()
        self.context = 'default'
        self.nete_client = nete_client

    @property
    def prompt(self):
        return 'nete [%s]> ' % self.context

    def do_ls(self, line):
        '''ls    list notes'''
        notes = self.nete_client.list()
        for note in notes:
            print('{id}   {title}'.format(**note))

    def do_cat(self, line):
        '''cat NOTE-ID [NOTE-ID…]   print note(s)'''
        note_ids = self._parse(line)
        for note_id in note_ids:
            try:
                note = self.nete_client.get_note(note_id)
                print(render_editable_note(note))
            except NotFound:
                print('{} not found.'.format(note_id))

    def do_new(self, line):
        '''new    create note'''
        title = input('Enter title for new note: ')
        note = {
            'id': None,
            'title': title,
            'text': '',
        }
        changed_note = edit_note(note)
        note = self.nete_client.create_note(changed_note)
        print('Created note with id {}'.format(note['id']))

    def do_edit(self, line):
        '''edit NAME    edit note NAME'''
        note_id = self._parse(line)[0]
        try:
            note = self.nete_client.get_note(note_id)
            changed_note = edit_note(note)
            self.nete_client.update_note(changed_note)
        except NotFound:
            print('Cannot edit {}, not found.'.format(note_id))

    def do_rm(self, line):
        '''rm NAME    remove note NAME'''
        note_ids = self._parse(line)
        for note_id in note_ids:
            try:
                self.nete_client.delete_note(note_id)
            except NotFound:
                print('Cannot remove {}, not found.'.format(note_id))

    def do_grep(self, line):
        '''grep REGEXP    search notes with REGEXP'''
        print('searching')

    def do_exit(self, line):
        '''exit    exit nete repl'''
        return True
    do_q = do_exit

    def do_context(self, line):
        '''context NAME    switch to context NAME'''
        self.context = line

    def do_EOF(self, line):
        return True

    def emptyline(self):
        pass

    def _parse(self, line):
        return line.split()

    def _complete_note_id_or_title(self, text, line, begidx, endidx):
        notes = self.nete_client.list()
        return (
            [note['id']
             for note in notes
             if text == '' or note['id'].startswith(text)])

    complete_cat = _complete_note_id_or_title
    complete_edit = _complete_note_id_or_title
    complete_rm = _complete_note_id_or_title


def edit_note(note):
    with tempfile.NamedTemporaryFile(prefix='nete') as fp:
        fp.write(render_editable_note(note).encode('utf-8'))
        fp.flush()
        result = subprocess.run(
            '{} {}'.format(os.environ.get('EDITOR'), fp.name),
            shell=True)
        if result.returncode == 0:
            # FIXME: what do to else?
            fp.seek(0)
            data = fp.read().decode('utf-8')
            note.update(parse_editable_note(data, note))
            return note


def render_editable_note(note):
    return '''Title: {title}
Id: {id}
Created-At: {created_at}
Updated-At: {updated_at}

{text}'''.format(
    id=note['id'],
    title=note['title'],
    created_at=note.get('created_at', '<not set>'),
    updated_at=note.get('updated_at', '<not set>'),
    text=note['text']
    )


def parse_editable_note(formatted_note, original_note):
    header_data, text = formatted_note.split('\n\n', 1)
    headers = {
        key: value
        for key, value in map(
            lambda line: re.split(': *', line, 1),
            header_data.splitlines())
    }

    attrs = {
        'title': headers.get('Title'),
        'text': text,
    }

    return {
        key: value for key, value in attrs.items() if value is not None
    }

