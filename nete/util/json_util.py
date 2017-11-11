import datetime
import dateutil.parser
import json


def default_serialize(obj):
    """
    Serialize function for use as `default` parameter in `json.dump`.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    raise TypeError('Cannot serialize object of type {}'.format(type(obj)))


def note_object_hook(obj):
    """
    Object hook for use with `json.load`.
    """
    if obj.get('created_at'):
        obj['created_at'] = dateutil.parser.parse(obj['created_at'])

    if obj.get('updated_at'):
        obj['updated_at'] = dateutil.parser.parse(obj['updated_at'])

    return obj
