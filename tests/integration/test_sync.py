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
    # create on local side
    local_editor.set_content('Title: NEW NOTE\n\nFOO')
    out, err = local_nete('new', 'NEW NOTE')
    mo = re.match(r'Created note with id (.*)', out)
    note_id = mo.group(1)

    # sync
    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    out, err = remote_nete('ls')
    assert out == '{}   NEW NOTE\n'.format(note_id)


def test_sync_copies_remote_new_note_to_local(
        local_backend, remote_backend, remote_editor,
        remote_nete, local_nete):
    # create on remote side
    remote_editor.set_content('Title: NEW NOTE\n\nFOO')
    out, err = remote_nete('new', 'NEW NOTE')
    mo = re.match(r'Created note with id (.*)', out)
    note_id = mo.group(1)

    # sync
    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    out, err = local_nete('cat', note_id)
    assert err == ''
    assert 'Title: NEW NOTE\n' in out
    assert out.endswith('\n\nFOO\n'), '»{}« should end with »FOO«, but didn’t'.format(out)


def test_sync_updates_remote_note_if_changed_locally(
        local_backend, remote_backend,
        local_editor, remote_editor,
        remote_nete, local_nete):
    # create on remote side
    local_editor.set_content('Title: TITLE\n\nFOO')
    out, err = local_nete('new', 'TITLE')
    mo = re.match(r'Created note with id (.*)', out)
    note_id = mo.group(1)

    # sync
    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    # edit locally
    local_editor.set_content('Title: OTHER TITLE\n\nBAR')
    out, err = local_nete('edit', note_id)
    assert err == ''

    # sync again
    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    out, err = remote_nete('cat', note_id)
    assert err == ''
    assert 'Title: OTHER TITLE\n' in out
    assert out.endswith('\n\nBAR\n'), '»{}« should end with »FOO«, but didn’t'.format(out)


def test_sync_updates_local_note_if_changed_remotely(
        local_backend, remote_backend,
        local_editor, remote_editor,
        remote_nete, local_nete):
    # create on remote side
    local_editor.set_content('Title: TITLE\n\nFOO')
    out, err = local_nete('new', 'TITLE')
    mo = re.match(r'Created note with id (.*)', out)
    note_id = mo.group(1)

    # sync
    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    # edit remotely
    remote_editor.set_content('Title: OTHER TITLE\n\nBAR')
    out, err = remote_nete('edit', note_id)
    assert err == ''

    # sync again
    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    out, err = local_nete('cat', note_id)
    assert err == ''
    assert 'Title: OTHER TITLE\n' in out
    assert out.endswith('\n\nBAR\n'), '»{}« should end with »BAR«, but didn’t'.format(out)


def test_sync_creates_copy_of_conflicting_local_note_and_returns_its_id(
        local_backend, remote_backend,
        local_editor, remote_editor,
        remote_nete, local_nete):
    # create on remote side
    local_editor.set_content('Title: TITLE\n\nFOO')
    out, err = local_nete('new', 'TITLE')
    mo = re.match(r'Created note with id (.*)', out)
    note_id = mo.group(1)

    # sync
    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    # edit locally
    local_editor.set_content('Title: LOCAL TITLE\n\nLOCAL TEXT')
    out, err = local_nete('edit', note_id)
    assert err == ''

    # edit remotely
    remote_editor.set_content('Title: REMOTE TITLE\n\nREMOTE TEXT')
    out, err = remote_nete('edit', note_id)
    assert err == ''

    # sync again
    out, err = local_nete('sync')
    assert err == ''
    assert local_nete.returncode() == 0

    # local result
    out, err = local_nete('cat', note_id)
    assert err == ''
    assert 'Title: REMOTE TITLE\n' in out
    assert out.endswith('\n\nREMOTE TEXT\n'), '»{}« should end with »REMOTE TEXT«, but didn’t'.format(out)

    out, err = local_nete('ls')
    mo = re.match(r'(.*)   LOCAL TITLE\n(.*)   REMOTE TITLE\n', out)
    assert mo, '»{}« wasn’t matched'.format(out).format(out)
    conflict_copy_id = mo.group(1)
    assert mo.group(2) == note_id

    out, err = local_nete('cat', conflict_copy_id)
    assert err == ''
    assert out.endswith('\n\nLOCAL TEXT\n'), '»{}« should end with »LOCAL TEXT«, but it didn’t'.format(out)

    # remote result
    out, err = remote_nete('cat', note_id)
    assert err == ''
    assert 'Title: REMOTE TITLE\n' in out
    assert out.endswith('\n\nREMOTE TEXT\n'), '»{}« should end with »REMOTE TEXT«, but didn’t'.format(out)

    out, err = remote_nete('ls')
    mo = re.match(r'(.*)   LOCAL TITLE\n(.*)   REMOTE TITLE\n', out)
    assert mo, '»{}« wasn’t matched'.format(out).format(out)
    conflict_copy_id = mo.group(1)
    assert mo.group(2) == note_id

    out, err = remote_nete('cat', conflict_copy_id)
    assert err == ''
    assert out.endswith('\n\nLOCAL TEXT\n'), '»{}« should end with »LOCAL TEXT«, but it didn’t'.format(out)
