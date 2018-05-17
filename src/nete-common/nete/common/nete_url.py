from enum import Enum
from urllib.parse import urlparse

class ConnectionType(Enum):
    TCP = 1
    UNIX = 2
    SSH = 3


class NeteUrl:

    def __init__(self, connection_type, base_url=None, socket_path=None,
                 ssh_host=None, ssh_port=None, username=None):
        if connection_type not in list(ConnectionType):
            raise ConnectionTypeNotSupported(connection_type)

        self.connection_type = connection_type
        self.base_url = base_url
        self.socket_path = socket_path
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port or 22
        self.username = username

    @classmethod
    def from_string(cls, url):
        parsed_url = urlparse(url)
        connection_type = parsed_url.scheme

        if connection_type in ('http', 'https'):
            return cls(ConnectionType.TCP,
                       base_url=url)
        elif connection_type == 'local':
            return cls(ConnectionType.UNIX,
                       socket_path=parsed_url.path)
        elif connection_type == 'http+ssh':
            return cls(ConnectionType.SSH,
                       ssh_host=parsed_url.hostname,
                       ssh_port=parsed_url.port,
                       username=parsed_url.username)
        else:
            raise ConnectionTypeNotSupported(connection_type)

    def __str__(self):
        return '<NeteUrl connection_type={} base_url={} socket_path={} ssh_host={} ssh_port={} username={}>'.format(
            self.connection_type, self.base_url, self.socket_path,
            self.ssh_host, self.ssh_port, self.username)


class ConnectionTypeNotSupported(Exception):

    def __init__(self, connection_type):
        self.connection_type = connection_type

    def __str__(self):
        return 'Connection type »{}« not supported'.format(self.connection_type)
