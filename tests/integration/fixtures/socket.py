import os.path
import pytest
import tempfile


def make_socket_fixture():
    def socket():
        with tempfile.TemporaryDirectory() as sock_tmp_dir:
            yield os.path.join(sock_tmp_dir, 'nete.sock')
    return pytest.fixture(socket)
