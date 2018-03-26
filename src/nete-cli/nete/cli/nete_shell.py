from .edit_note import edit_note, render_editable_note
from .nete_client import NotFound
from nete.common.models import Note
import uuid


class NeteShell:
    def __init__(self, nete_client):
        self.nete_client = nete_client

    def run(self, args):
        cmd_kwargs = {
            key: getattr(args, key)
            for key in args.options
        }
        getattr(self, '{}'.format(args.cmd))(**cmd_kwargs)

    def cat(self, note_ids):
        for note_id in note_ids:
            try:
                note = self.nete_client.get_note(uuid.UUID(note_id))
                print(render_editable_note(note))
            except NotFound:
                print('{} not found.'.format(note_id))

    def edit(self, note_id):
        try:
            note = self.nete_client.get_note(uuid.UUID(note_id))
            changed_note = edit_note(note)
            self.nete_client.update_note(changed_note)
        except NotFound:
            print('Cannot edit {}, not found.'.format(note_id))

    def ls(self):
        notes = self.nete_client.list()
        for note in notes:
            print('{id}   {title}'.format(**note.__dict__))

    def new(self, title):
        note = Note(title=title, text='')
        changed_note = edit_note(note)
        note = self.nete_client.create_note(changed_note)
        print('Created note with id {}'.format(note.id))

    def rm(self, note_ids):
        for note_id in note_ids:
            try:
                self.nete_client.delete_note(uuid.UUID(note_id))
            except NotFound:
                print('Cannot remove {}, not found.'.format(note_id))

    def complete_note_id_or_title(self, text):
        notes = self.nete_client.list()
        return (
            [str(note.id)
             for note in notes
             if text == '' or str(note.id).startswith(text)])
