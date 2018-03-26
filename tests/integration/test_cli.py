from tools.spawn import spawn
from nete.cli.test_utils.editor import Editor
import os
import os.path
import pexpect
import pytest
import subprocess
import tempfile


@pytest.fixture
def socket():
    with tempfile.TemporaryDirectory() as sock_tmp_dir:
        yield os.path.join(sock_tmp_dir, 'nete.sock')


@pytest.fixture
def cli_config(socket):
    with tempfile.NamedTemporaryFile() as config_file:
        config_file.write('[backend]\nurl = local:{}'
                          .format(socket)
                          .encode('utf-8'))
        config_file.flush()
        yield config_file.name


@pytest.fixture
def server(socket):
    with tempfile.TemporaryDirectory() as tmp_dir:
        process = pexpect.spawn(
            'nete-backend '
            '--no-rc '
            '--storage filesystem '
            '--storage-base-dir {storage_base_dir} '
            '--api-socket {socket}'
            .format(storage_base_dir=tmp_dir, socket=socket),
            logfile=open('/tmp/pexpect-server.log', 'wb'),
            timeout=5)
        process.expect('.*Starting server on.*')
        yield

        process.terminate()
        try:
            process.wait()
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


@pytest.fixture
def editor():
    with Editor() as editor:
        yield editor


@pytest.fixture
def run_nete(server, editor, socket, cli_config):
    def run_nete(*args):
        env = os.environ.copy()
        env.update(editor.env())
        env['NETE_CONFIG_FILE'] = cli_config
        return spawn(
            'nete',
            list(args),
            env=env,
            timeout=2)
    return run_nete


def test_new_and_ls(server, run_nete, editor):
    editor.set_content('Title: NEW NOTE\n\nFOO')
    proc = run_nete('new', 'NEW NOTE')
    proc.assertExpect('Created note with id (.*)')
    note_id = proc.match[1].split()[0].decode('utf-8')
    proc.assertExpect(pexpect.EOF)

    proc = run_nete('ls')
    proc.assertExpect('{}   NEW NOTE'.format(note_id))
    proc.assertExpect(pexpect.EOF)


def test_new_and_cat(server, run_nete, editor):
    editor.set_content('Title: NEW NOTE\n\nFOO')
    proc = run_nete('new', 'NEW NOTE')
    proc.assertExpect('Created note with id (.*)')
    note_id = proc.match[1].split()[0].decode('utf-8')
    proc.assertExpect(pexpect.EOF)

    proc = run_nete('cat', note_id)
    proc.assertExpect('.*FOO')
    proc.assertExpect(pexpect.EOF)


def test_edit(server, run_nete, editor):
    editor.set_content('Title: NEW NOTE\n\nFOO')
    proc = run_nete('new', 'NEW NOTE')
    proc.assertExpect('Created note with id (.*)')
    note_id = proc.match[1].split()[0].decode('utf-8')
    proc.assertExpect(pexpect.EOF)

    editor.set_content('Title: NEW NOTE\n\nBAR')
    proc = run_nete('edit', note_id)
    proc.assertExpect(pexpect.EOF)

    proc = run_nete('cat', note_id)
    proc.assertExpect('.*BAR')
    proc.assertExpect(pexpect.EOF)
