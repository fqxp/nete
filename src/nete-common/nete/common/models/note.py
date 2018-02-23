class Note:
    def __init__(self, id=None, created_at=None, updated_at=None, title='',
                 text=''):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.title = title
        self.text = text

    def __repr__(self):
        return 'Note(id={})'.format(str(self.id))
