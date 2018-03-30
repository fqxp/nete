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
        note_ids = line.split()
        self.shell.cat(note_ids)

    def do_edit(self, line):
        '''edit NAME    edit note NAME'''
        note_id = line.split()[0]
        self.shell.edit(note_id)

    def do_new(self, line):
        '''new    create note'''
        title = input('Enter title for new note: ')
        self.shell.new(title)

    def do_rm(self, line):
        '''rm NAME    remove note NAME'''
        note_ids = line.split()
        self.shell.rm(note_ids)

    def do_exit(self, line):
        '''exit    exit nete repl'''
        return True

    def do_EOF(self, line):
        return True

    def emptyline(self):
        pass

    def _complete_note_id(self, text, line, begidx, endidx):
        return self.shell.complete_note_id(text)

    complete_cat = _complete_note_id
    complete_edit = _complete_note_id
    complete_rm = _complete_note_id
