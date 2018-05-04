from urllib.parse import urlparse


class NeteUrl:

    def __init__(self, connection_type, base_url=None, socket_path=None):
        if connection_type not in ('local', 'http', 'https', 'http+ssh'):
            raise ConnectionTypeNotSupported(connection_type)

        self.connection_type = connection_type
        self.base_url = base_url
        self.socket_path = socket_path

    @classmethod
    def from_string(cls, url):
        parsed_url = urlparse(url)


        connection_type = parsed_url.scheme
        base_url = url if connection_type in ('http', 'https') else None
        socket_path = parsed_url.path if connection_type == 'local' else None
        return cls(connection_type, base_url, socket_path)

    def is_socket_url(self):
        return self.connection_type == 'local'

    def is_ssh_url(self):
        return self.connection_type == 'http+ssh'

    def is_http_url(self):
        return self.connection_type in ('http', 'https')

    def __str__(self):
        return '<NeteUrl connection_type={} base_url={} socket_path={}>'.format(
            self.connection_type, self.base_url, self.socket_path)


class ConnectionTypeNotSupported(Exception):

    def __init__(self, connection_type):
        self.connection_type = connection_type

    def __str__(self):
        return 'Connection type »{}« not supported'.format(self.connection_type)
