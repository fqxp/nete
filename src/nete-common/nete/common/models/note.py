class Note:
    def __init__(self, id=None, created_at=None, updated_at=None, title='',
                 text=''):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.title = title
        self.text = text

    def __eq__(self, other):
        return (
            self.id == other.id and
            self.created_at == other.created_at and
            self.updated_at == other.updated_at and
            self.title == other.title and
            self.text == other.text
            )

    def __repr__(self):
        return 'Note(id={})'.format(str(self.id))
