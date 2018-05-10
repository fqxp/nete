from .edit_note import edit_note, render_editable_note
from .nete_client import NotFound
from nete.common.models import Note
from nete.common.nete_url import NeteUrl
import uuid


class NeteShell:
    def __init__(self, nete_client, config):
        self.nete_client = nete_client
        self.config = config

    def run(self, args):
        cmd_kwargs = {
            key: getattr(args, key)
            for key in args.options
        }
        return getattr(self, '{}'.format(args.cmd))(**cmd_kwargs)

    def cat(self, note_ids):
        for note_id in note_ids:
            try:
                note = self.nete_client.get_note(uuid.UUID(note_id))
                print(render_editable_note(note))
                return 0
            except NotFound:
                print('{} not found.'.format(note_id))
                return 1

    def edit(self, note_id):
        try:
            note = self.nete_client.get_note(uuid.UUID(note_id))
            changed_note = edit_note(note)
            changed_note.revision_id = uuid.uuid4()
            self.nete_client.update_note(
                changed_note,
                old_revision_id=note.revision_id)
            return 0
        except NotFound:
            print('Cannot edit {}, not found.'.format(note_id))
            return 1

    def ls(self):
        notes = self.nete_client.list()
        sort_fn = lambda note: note.title
        for note in sorted(notes, key=sort_fn):
            print('{id}   {title}'.format(**note.__dict__))
        return 0

    def new(self, title):
        note = Note(id=uuid.uuid4(),
                    revision_id=uuid.uuid4(),
                    title=title,
                    text='')
        changed_note = edit_note(note)
        note = self.nete_client.create_note(changed_note)
        print('Created note with id {}'.format(note.id))
        return 0

    def rm(self, note_ids):
        for note_id in note_ids:
            try:
                self.nete_client.delete_note(uuid.UUID(note_id))
                return 0
            except NotFound:
                print('Cannot remove {}, not found.'.format(note_id))
                return 1

    def sync(self):
        self.nete_client.sync()

    def socket(self):
        nete_url = NeteUrl.from_string(self.config['backend.url'])
        if nete_url.is_socket_url():
            print(nete_url.socket_path)
            return 0
        else:
            return 1

    def complete_note_id(self, text):
        notes = self.nete_client.list()
        return (
            [str(note.id)
             for note in notes
             if text == '' or str(note.id).startswith(text)])
