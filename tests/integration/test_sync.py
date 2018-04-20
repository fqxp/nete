from tools.pytest_io import pytest_io
from fixtures.socket import make_socket_fixture
from fixtures.backend import backend
from fixtures.config import config_fixture
from nete.cli.test_utils.editor import Editor
import os
import pytest
import re
import tempfile


local_socket = make_socket_fixture()
remote_socket = make_socket_fixture()


@pytest.fixture
def local_cli_config(local_socket):
    config = {
        'backend': {
            'url': 'local:{}'.format(local_socket),
        }
    }
    with config_fixture(config) as filename:
        yield filename


@pytest.fixture
def remote_cli_config(remote_socket):
    config = {
        'backend': {
            'url': 'local:{}'.format(remote_socket),
        }
    }
    with config_fixture(config) as filename:
        yield filename


@pytest.fixture
def local_backend_config(local_socket, remote_socket):
    with tempfile.TemporaryDirectory() as storage_base_dir:
        config = {
            'api': {
                'socket': local_socket,
            },
            'storage': {
                'type': 'filesystem',
                'base_dir': storage_base_dir,
            },
            'sync': {
                'url': 'local:{}'.format(remote_socket),
            },
        }
        with config_fixture(config) as filename:
            yield filename


@pytest.fixture
def remote_backend_config(remote_socket):
    with tempfile.TemporaryDirectory() as storage_base_dir:
        config = {
            'api': {
                'socket': remote_socket,
            },
            'storage': {
                'type': 'filesystem',
                'base_dir': storage_base_dir,
            },
        }
        with config_fixture(config) as filename:
            yield filename


@pytest.fixture
def local_backend(local_backend_config):
    with backend(local_backend_config, prefix='local_backend') as process:
        yield process


@pytest.fixture
def remote_backend(remote_backend_config):
    with backend(remote_backend_config, prefix='remote_backend') as process:
        yield process


@pytest.fixture
def local_editor():
    with Editor() as editor:
        yield editor


@pytest.fixture
def remote_editor():
    with Editor() as editor:
        yield editor


@pytest.fixture
def local_nete(local_editor, local_cli_config):
    env = {
        **os.environ,
        **local_editor.env(),
        'NETE_CONFIG_FILE': local_cli_config
    }
    return pytest_io('nete', env=env)


@pytest.fixture
def remote_nete(remote_editor, remote_cli_config):
    env = {
        **os.environ,
        **remote_editor.env(),
        'NETE_CONFIG_FILE': remote_cli_config
    }
    return pytest_io('nete', env=env)




def test_sync_copies_local_new_note_to_remote(
        local_backend, remote_backend, local_editor,
        remote_nete, local_nete):

    local_editor.set_content('Title: NEW NOTE\n\nFOO')
    out, err = local_nete('new', 'NEW NOTE')
    mo = re.match(r'Created note with id (.*)', out)
    note_id = mo.group(1)

    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    out, err = remote_nete('ls')
    assert out == '{}   NEW NOTE\n'.format(note_id)


def test_sync_copies_remote_new_note_to_local(
        local_backend, remote_backend, remote_editor,
        remote_nete, local_nete):
    remote_editor.set_content('Title: NEW NOTE\n\nFOO')
    out, err = remote_nete('new', 'NEW NOTE')
    mo = re.match(r'Created note with id (.*)', out)
    note_id = mo.group(1)

    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    out, err = local_nete('ls')
    assert out == '{}   NEW NOTE\n'.format(note_id)


# def test_sync_copies_remote_new_note_to_local(
#         remote_backend, local_backend, remote_editor,
#         remote_nete, local_nete):
#     remote_editor.set_content('Title: NEW NOTE\n\nFOO')
#     proc = remote_nete('new', 'NEW NOTE')
#     proc.assertExpect('Created note with id (.*)')
#     note_id = proc.match[1].split()[0].decode('utf-8')
#     proc.assertExpect(pexpect.EOF)

#     proc = remote_nete('sync')
#     proc.assertExpect(pexpect.EOF)

#     proc = local_nete('ls')
#     proc.assertExpect('{}   NEW NOTE'.format(note_id))
#     proc.assertExpect(pexpect.EOF)


# def test_sync_updates_remote_note_if_updated_locally(
#         remote_backend, local_backend, remote_editor,
#         local_editor, remote_nete, local_nete):
#     local_editor.set_content('Title: NEW NOTE\n\nFOO')
#     proc = local_nete('new', 'NEW NOTE')
#     proc.assertExpect('Created note with id (.*)')
#     note_id = proc.match[1].split()[0].decode('utf-8')
#     proc.assertExpect(pexpect.EOF)

#     proc = local_nete('sync')
#     proc.assertExpect(pexpect.EOF)

#     proc = remote_nete('ls')
#     proc.assertExpect('{}   NEW NOTE'.format(note_id))
#     proc.assertExpect(pexpect.EOF)

#     remote_editor.set_content('Title: CHANGED NOTE\n\nBAR')
#     proc = remote_nete('edit', note_id)
#     proc.assertExpect(pexpect.EOF)

#     proc = local_nete('sync')
#     proc.assertExpect(pexpect.EOF)

#     proc = local_nete('ls')
#     proc.assertExpect('{}   CHANGED NOTE'.format(note_id))
#     proc.assertExpect(pexpect.EOF)
