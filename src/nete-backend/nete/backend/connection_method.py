from nete.common.exceptions import SshError
from nete.common.nete_url import NeteUrl
from nete.common.xdg import XDG_RUNTIME_DIR
import aiohttp
import asyncssh
import logging
import os.path
import tempfile

logger = logging.getLogger(__name__)


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
