from tools.pytest_io import pytest_io
from fixtures.socket import make_socket_fixture
from fixtures.backend import backend
from fixtures.config import config_fixture
from nete.cli.test_utils.editor import Editor
import os
import pytest
import re
import tempfile

socket = make_socket_fixture()


@pytest.fixture
def backend_config(socket):
    with tempfile.TemporaryDirectory() as storage_base_dir:
        config = {
            'api': {
                'socket': socket,
            },
            'storage': {
                'type': 'filesystem',
                'base_dir': storage_base_dir,
            },
        }
        with config_fixture(config) as filename:
            yield filename


@pytest.fixture
def local_backend(backend_config):
    with backend(backend_config):
        yield


@pytest.fixture
def cli_config(socket):
    config = {
        'backend': {
            'url': 'local:{}'.format(socket),
        }
    }
    with config_fixture(config) as filename:
        yield filename


@pytest.fixture
def editor():
    with Editor() as editor:
        yield editor


@pytest.fixture
def nete(editor, cli_config):
    env = {
        **os.environ,
        **editor.env(),
        'NETE_CONFIG_FILE': cli_config,
    }
    return pytest_io('nete', env=env)


def test_new_and_ls(local_backend, cli_config, nete, editor):
    out, err = nete('new', 'NEW NOTE')
    assert err == ''
    mo = re.match(r'Created note with id (.*)', out)
    assert nete.returncode() == 0
    assert mo is not None
    note_id = mo.group(1)

    out, err = nete('ls')
    assert err == ''
    assert nete.returncode() == 0
    assert out == '{}   NEW NOTE\n'.format(note_id)


def test_new_and_cat(local_backend, nete, editor):
    editor.set_content('Title: NEW NOTE\n\nFOO')
    out, err = nete('new', 'NEW NOTE')
    mo = re.match(r'Created note with id (.*)', out)
    assert mo is not None
    note_id = mo.group(1)

    out, err = nete('cat', note_id)
    assert err == ''
    assert out.endswith('\n\nFOO\n')


def test_edit(local_backend, nete, editor):
    editor.set_content('Title: NEW NOTE\n\nFOO')
    out, err = nete('new', 'NEW NOTE')
    mo = re.match(r'Created note with id (.*)', out)
    assert mo is not None
    note_id = mo.group(1)

    editor.set_content('Title: NEW NOTE\n\nBAR')
    out, err = nete('edit', note_id)
    assert nete.returncode() == 0

    out, err = nete('cat', note_id)
    assert out.endswith('\n\nBAR\n')
