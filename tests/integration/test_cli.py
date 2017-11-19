from tools.spawn import spawn
from tools.editor import Editor
import os
import pexpect
import pytest
import subprocess
import tempfile


@pytest.fixture
def server():
    with tempfile.TemporaryDirectory() as tmp_dir:
        process = pexpect.spawn(
            'nete-backend --storage filesystem --storage-base-dir {}'.format(tmp_dir),
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
    editor = Editor()
    yield editor
    editor.cleanup()


@pytest.fixture
def client(editor):
    env = os.environ.copy()
    env.update(editor.env())
    return spawn(
        'nete',
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
