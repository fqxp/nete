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
def server(socket):
    with tempfile.TemporaryDirectory() as tmp_dir:
        process = pexpect.spawn(
            'nete-backend '
            '--no-rc '
            '--storage filesystem '
            '--storage-base-dir {storage_base_dir} '
            '--api-socket {socket}'
            .format(storage_base_dir=tmp_dir, socket=socket),
            logfile=open('/tmp/pexpect-server.log', 'wb'))
        process.expect('.*starting server on.*')
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
def client(editor, socket):
    env = os.environ.copy()
    env.update(editor.env())
    return spawn(
        'nete --no-rc --backend-url local:{}'.format(socket),
        env=env,
        timeout=2)


def test_cli(server, client, editor):
    # ls
    client.assertExpect(r'nete .*> ')
    client.sendline('ls')

    # new
    client.assertExpect(r'nete .*> ')
    editor.set_content('Title: abc\n\nFOO')
    client.sendline('new')
    client.assertExpect('Enter title.*: ')
    client.sendline('abc')
    client.assertExpect('Created note with id (.*)')
    note_id = client.match[1].split()[0]

    # cat
    client.assertExpect(r'nete .*> ')
    client.sendline('cat {}'.format(note_id.decode('utf-8')))
    client.assertExpect('.*FOO')

    # edit
    client.assertExpect(r'nete .*> ')
    editor.set_content('Title: abc\n\nBAR')
    client.sendline('edit {}'.format(note_id.decode('utf-8')))

    client.assertExpect(r'nete .*> ')
    client.sendline('cat {}'.format(note_id.decode('utf-8')))
    client.assertExpect('.*BAR')

    # exit
    client.assertExpect(r'nete .*> ')
    client.sendline('exit')
    client.assertExpect(pexpect.EOF)
