from nete.common.xdg import XDG_RUNTIME_DIR
import aiohttp
import asyncssh
import os
import logging
import tempfile

logger = logging.getLogger(__name__)


class SshError(Exception):
    def __init__(self, message):
        self.message = message


class SshConnector(aiohttp.UnixConnector):

    def __init__(self, host, port, username, **kwargs):
        self.host = host
        self.port = port if port else 22
        self.username = username
        self.tempdir = tempfile.mkdtemp('nete-ssh', dir=XDG_RUNTIME_DIR)
        local_socket_path = os.path.join(self.tempdir, 'ssh.socket')
        super().__init__(local_socket_path, **kwargs)

    async def connect(self, *args, **kwargs):
        logger.info('entering SshConnector')

        logger.info('Opening SSH connection {}@{}:{}'.format(
            self.username, self.host, self.port))
        self.ssh_conn = await asyncssh.connect(
            self.host, self.port, username=self.username)
        try:
            result = await self.ssh_conn.run(command='nete socket', check=True)
            remote_socket_path = result.stdout.strip()
            logger.debug('remote socket is »{}«'.format(remote_socket_path))
        except asyncssh.ProcessError:
            raise SshError('Could not find out socket path on remote side (output of »nete socket« was: {}'.format(result.stdout))

        await self.ssh_conn.forward_local_path(
            self.path, remote_socket_path)

        return await super().connect(*args, **kwargs)

    def close(self, *args, **kwargs):
        logger.info('exiting SshConnector')
        super().close(*args, **kwargs)

        self.ssh_conn.close()
        os.remove(self.path)
        os.removedirs(self.tempdir)
