from nete.common.models import Note
from .nete_client import NotFound, ServerError
from .edit_note import edit_note, render_editable_note
import cmd
import uuid


class Repl(cmd.Cmd):

    def __init__(self, nete_client):
        super().__init__()
        self.context = 'default'
        self.nete_client = nete_client

    @property
    def prompt(self):
        return 'nete [%s]> ' % self.context

    def onecmd(self, s):
        try:
            return super().onecmd(s)
        except ServerError as e:
            print('Error while communication with backend: {}'.format(e.error))

    def do_ls(self, line):
        '''ls    list notes'''
        notes = self.nete_client.list()
        for note in notes:
            print('{id}   {title}'.format(**note.__dict__))

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
        note = Note(title=title, text='')
        changed_note = edit_note(note)
        note = self.nete_client.create_note(changed_note)
        print('Created note with id {}'.format(note.id))

    def do_edit(self, line):
        '''edit NAME    edit note NAME'''
        note_id = self._parse(line)[0]
        try:
            note = self.nete_client.get_note(uuid.UUID(note_id))
            changed_note = edit_note(note)
            self.nete_client.update_note(changed_note)
        except NotFound:
            print('Cannot edit {}, not found.'.format(note_id))

    def do_rm(self, line):
        '''rm NAME    remove note NAME'''
        note_ids = self._parse(line)
        for note_id in note_ids:
            try:
                self.nete_client.delete_note(uuid.UUID(note_id))
            except NotFound:
                print('Cannot remove {}, not found.'.format(note_id))

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
            [str(note.id)
             for note in notes
             if text == '' or str(note.id).startswith(text)])

    complete_cat = _complete_note_id_or_title
    complete_edit = _complete_note_id_or_title
    complete_rm = _complete_note_id_or_title