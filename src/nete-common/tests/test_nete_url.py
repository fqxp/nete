from nete.common.nete_url import NeteUrl, ConnectionTypeNotSupported
import pytest


def test_from_string_with_local_url():
    nete_url = NeteUrl.from_string('local:/tmp/socket')
    assert nete_url.is_socket_url()
    assert not nete_url.is_http_url()
    assert not nete_url.is_ssh_url()
    assert nete_url.base_url is None
    assert nete_url.socket_path == '/tmp/socket'


@pytest.mark.parametrize('scheme', ['http', 'https'])
def test_from_string_with_http_url(scheme):
    nete_url = NeteUrl.from_string('{}://nete.io/path'.format(scheme))
    assert not nete_url.is_socket_url()
    assert nete_url.is_http_url()
    assert not nete_url.is_ssh_url()
    assert nete_url.base_url == '{}://nete.io/path'.format(scheme)
    assert nete_url.socket_path is None


def test_from_string_with_ssh_url():
    nete_url = NeteUrl.from_string('http+ssh://user@example.org:2222')
    assert nete_url.is_ssh_url()
    assert not nete_url.is_socket_url()
    assert not nete_url.is_http_url()
    assert nete_url.base_url is None
    assert nete_url.socket_path is None
    assert nete_url.ssh_host == 'example.org'
    assert nete_url.ssh_port == 2222
    assert nete_url.username == 'user'


def test_from_string_raises_with_unsupported_scheme():
    with pytest.raises(ConnectionTypeNotSupported):
        NeteUrl.from_string('unsupported:/tmp/socket')
