from marshmallow import Schema, fields, post_load
from nete.common.models.note import Note
import datetime
import uuid


class NoteSchema(Schema):
    id = fields.UUID(required=True, allow_none=False, missing=uuid.uuid4)
    created_at = fields.DateTime(
        required=True,
        allow_none=False,
        missing=lambda: datetime.datetime.utcnow().isoformat())
    updated_at = fields.DateTime(
        required=True,
        allow_none=False,
        missing=lambda: datetime.datetime.utcnow().isoformat())
    title = fields.Str(required=True)
    text = fields.Str(required=True)

    @post_load
    def make_object(self, data):
        return Note(**data)
