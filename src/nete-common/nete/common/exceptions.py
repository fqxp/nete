class NeteException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NotFound(NeteException):
    pass


class ServerError(NeteException):
    pass


class SshError(NeteException):
    pass
