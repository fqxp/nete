from .connection_method import TcpConnectionMethod, SocketConnectionMethod, SshConnectionMethod
from nete.common.nete_url import ConnectionType
from nete.common.exceptions import ServerError
from nete.common.schemas.note_schema import NoteSchema
from nete.common.schemas.note_index_schema import NoteIndexSchema
from urllib.parse import urljoin
import aiohttp
import logging

logger = logging.getLogger(__name__)

note_index_schema = NoteIndexSchema()
note_schema = NoteSchema()

CONNECTION_TYPE_MAPPING = {
    ConnectionType.TCP: TcpConnectionMethod,
    ConnectionType.UNIX: SocketConnectionMethod,
    ConnectionType.SSH: SshConnectionMethod,
}


class NeteClient:

    def __init__(self, remote_url):
        self.remote_url = remote_url
        self.connection_method = self.build_connection_method(remote_url)

    def build_connection_method(self, url):
        return CONNECTION_TYPE_MAPPING[url.connection_type](url)

    async def __aenter__(self):
         await self.connection_method.start()
         self.session = aiohttp.ClientSession(
             connector=self.connection_method.connector())
         return self

    async def __aexit__(self, *args):
        await self.session.close()
        await self.connection_method.stop()

    def build_url(self, path):
        return urljoin(self.connection_method.base_url, path)

    async def list_notes(self):
        response = await self.session.get(self.build_url('/notes'))
        text = await response.text()
        return note_index_schema.loads(text, many=True)

    async def create_note(self, note):
        url = self.build_url('/notes')
        data = note_schema.dumps(note)
        response = await self.session.post(
            url,
            headers={
                'content-type': 'application/json',
            },
            data=data)
        if response.status >= 400:
            raise ServerError(
                'Error during sync (create {}):\n{}'.format(
                    note.id, await response.text()))

    async def update_note(self, note, old_revision_id):
        url = self.build_url('/notes/{}'.format(note.id))
        data = note_schema.dumps(note)
        response = await self.session.put(
            url,
            headers={
                'content-type': 'application/json',
                'if-match': str(old_revision_id),
            },
            data=data)
        if response.status >= 400:
            raise ServerError(
                'Error updating note ({}):\n{}'.format(
                    note.id, await response.text()))

    async def get_note(self, note_id):
        url = self.build_url('/notes/{}'.format(str(note_id)))
        response = await self.session.get(url)

        if response.status >= 400:
            raise ServerError(
                'Error getting note ({}):\n{}'.format(
                    note_id, await response.text()))

        return note_schema.loads(await response.text())
