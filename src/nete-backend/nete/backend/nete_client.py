from nete.common.nete_url import NeteUrl
from nete.common.exceptions import ServerError
from nete.common.xdg import XDG_RUNTIME_DIR
from nete.common.schemas.note_index_schema import NoteIndexSchema
from nete.common.schemas.note_schema import NoteSchema
from urllib.parse import urljoin
import aiohttp
import asyncssh
import logging
import os.path
import tempfile

logger = logging.getLogger(__name__)

note_index_schema = NoteIndexSchema()
note_schema = NoteSchema()


class SshError(Exception):
    def __init__(self, message):
        self.message = message


class BaseConnectionMethod:
    def __init__(self, url: NeteUrl):
        self.url = url

    async def start(self):
        pass

    async def stop(self):
        pass


class TcpConnectionMethod(BaseConnectionMethod):

    @property
    def base_url(self):
        return self.url.base_url

    def connector(self):
        return aiohttp.TCPConnector()


class SocketConnectionMethod(BaseConnectionMethod):

    @property
    def base_url(self):
        return 'http://aiohttp'

    def connector(self):
        return aiohttp.UnixConnector(self.url.socket_path)


class SshConnectionMethod(BaseConnectionMethod):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tempdir = tempfile.mkdtemp('nete-ssh', dir=XDG_RUNTIME_DIR)
        self.local_socket = os.path.join(self.tempdir, 'ssh.socket')

    @property
    def base_url(self):
        return 'http://aiohttp'

    def connector(self):
        return aiohttp.UnixConnector(self.local_socket)

    async def start(self):
        logger.info('Opening SSH connection {}@{}:{}'.format(
            self.url.username, self.url.ssh_host, self.url.ssh_port))
        self.ssh_conn = await asyncssh.connect(
            self.url.ssh_host,
            self.url.ssh_port,
            username=self.url.username)
        remote_socket = await self._get_remote_socket()

        await self.ssh_conn.forward_local_path(
            self.local_socket, remote_socket)

    async def stop(self):
        logger.info('Closing SSH connection')

        self.ssh_conn.close()
        os.remove(self.local_socket)
        os.removedirs(self.tempdir)

    async def _get_remote_socket(self):
        try:
            result = await self.ssh_conn.run(
                command='nete socket', check=True)
            remote_socket = result.stdout.strip()
            logger.debug('remote socket is »{}«'.format(
                remote_socket))
            return remote_socket
        except asyncssh.ProcessError:
            message = (
                'Could not find out socket path on '
                'remote side '
                '(output of »nete socket« was: {}'.format(
                    result.stdout))
            raise SshError(message)


def build_connection_method(url: NeteUrl):
    if url.is_socket_url():
        cls = SocketConnectionMethod
    elif url.is_http_url():
        cls = TcpConnectionMethod
    elif url.is_ssh_url():
        cls = SshConnectionMethod

    return cls(url)


class NeteClient:

    def __init__(self, remote_url):
        self.remote_url = remote_url
        self.connection_method = build_connection_method(remote_url)

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
