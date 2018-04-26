from marshmallow import Schema, fields


class StatusItemSchema(Schema):

    note_id = fields.UUID()
    revision_id = fields.UUID()
