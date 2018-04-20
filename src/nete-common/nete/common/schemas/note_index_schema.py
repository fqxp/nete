from .note_schema import NoteSchema


class NoteIndexSchema(NoteSchema):
    class Meta:
        exclude = ('text',)
