from nete.common.exceptions import NotFound, ServerError
from nete.common.schemas.note_schema import NoteSchema
from nete.common.schemas.note_index_schema import NoteIndexSchema
from nete.common.nete_url import ConnectionType
import requests
import requests_unixsocket
import urllib.parse


class NeteClient:

    def __init__(self, backend_url):
        self._prepare_base_url(backend_url)
        self.note_schema = NoteSchema()
        self.note_index_schema = NoteIndexSchema()

    def _prepare_base_url(self, backend_url):
        if backend_url.connection_type == ConnectionType.UNIX:
            quoted_path = urllib.parse.quote(backend_url.socket_path, safe='')
            self.base_url = 'http+unix://{}'.format(quoted_path)
            self.session = requests_unixsocket.Session()
        elif backend_url.connection_type == ConnectionType.TCP:
            self.base_url = backend_url.base_url
            self.session = requests.Session()

    def list(self):
        response = self._get('/notes')
        return self.note_index_schema.loads(response.text, many=True)

    def get_note(self, note_id):
        response = self._get('/notes/{}', note_id)
        return self.note_schema.loads(response.text)

    def create_note(self, note):
        note_schema = NoteSchema(exclude=('created_at', 'updated_at'))
        response = self._post(
            '/notes',
            data=note_schema.dumps(note))
        return self.note_schema.loads(response.text)

    def update_note(self, note, old_revision_id):
        self._put(
            '/notes/{}'.format(note.id),
            headers={
                'if-match': str(old_revision_id),
            },
            data=self.note_schema.dumps(note))

    def delete_note(self, note_id):
        self._delete('/notes/{}', note_id)

    def sync(self):
        self._get('/notes/sync')

    def _get(self, path, *args, **kwargs):
        request = requests.Request(
            'GET',
            self._url(path, *args, **kwargs))
        return self._send(request)

    def _post(self, path, data, *args, **kwargs):
        request = requests.Request(
            'POST',
            self._url(path, *args, **kwargs),
            data=data)
        return self._send(request)

    def _put(self, path, data, *args, headers=None, **kwargs):
        request = requests.Request(
            'PUT',
            self._url(path, *args, **kwargs),
            headers=headers,
            data=data)
        return self._send(request)

    def _delete(self, path, *args, **kwargs):
        request = requests.Request(
            'DELETE',
            self._url(path, *args, **kwargs))
        return self._send(request)

    def _send(self, request):
        try:
            response = self.session.send(request.prepare())
            response.raise_for_status()
            return response
        except requests.HTTPError as exc:
            status_code = exc.response.status_code
            if status_code == 404:
                raise NotFound('URL {} not found'.format(request.url))
            else:
                raise ServerError(response.text)

    def _url(self, path, *args, **kwargs):
        path = path.lstrip('/').format(*args, **kwargs)
        return '{base_url}/{path}'.format(
            base_url=self.base_url,
            path=path)

    def __repr__(self):
        return '<NeteClient base_url={}>'.format(
            self.base_url)
