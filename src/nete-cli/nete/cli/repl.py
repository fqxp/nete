from .nete_client import ServerError
import cmd


class Repl(cmd.Cmd):

    def __init__(self, shell):
        super().__init__()
        self.shell = shell

    @property
    def prompt(self):
        return 'nete> '

    def onecmd(self, s):
        try:
            return super().onecmd(s)
        except ServerError as e:
            print('Error while communication with backend: {}'.format(e.error))

    def do_ls(self, line):
        '''ls    list notes'''
        self.shell.ls()

    def do_cat(self, line):
        '''cat NOTE-ID [NOTE-ID…]   print note(s)'''
        note_ids = self._parse(line)
        self.shell.cat(note_ids)

    def do_edit(self, line):
        '''edit NAME    edit note NAME'''
        note_id = self._parse(line)[0]
        self.shell.edit(note_id)

    def do_new(self, line):
        '''new    create note'''
        title = input('Enter title for new note: ')
        self.shell.new(title)

    def do_rm(self, line):
        '''rm NAME    remove note NAME'''
        note_ids = self._parse(line)
        self.shell.rm(note_ids)

    def do_exit(self, line):
        '''exit    exit nete repl'''
        return True

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
