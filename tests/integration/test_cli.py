import os
import pexpect
import pytest
import subprocess
import tempfile


@pytest.fixture
def server():
    process = pexpect.spawn('nete-backend',
                            logfile=open('.pexpect-server.log', 'wb'))
    process.expect('.*starting server on.*')
    yield
    process.terminate()
        print(
    try:
        process.wait()
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


class Editor:
    def __init__(self):
        self.content_fp = tempfile.NamedTemporaryFile()
        cmd_fp = tempfile.NamedTemporaryFile(delete=False)
        self.cmd_name = cmd_fp.name
        cmd_fp.write('#!/bin/bash\ncp {} $1'.format(self.content_fp.name, self.content_fp.name).encode('utf-8'))
        cmd_fp.close()
        os.chmod(self.cmd_name, 0o755)

    def env(self):
        return {'EDITOR': '/bin/bash {}'.format(self.cmd_name)}

    def set_content(self, content):
        self.content_fp.seek(0)
        self.content_fp.write(content.encode('utf-8'))
        self.content_fp.truncate()
        self.content_fp.flush()

    def cleanup(self):
        os.unlink(self.cmd_name)
        self.content_fp.close()


@pytest.fixture
def editor():
    editor = Editor()
    yield editor
    editor.cleanup()


@pytest.fixture
def client(editor):
    env = os.environ.copy()
    env.update(editor.env())
    return pexpect.spawn(
        'nete',
        env=env,
        echo=False,
        logfile=open('./.pexpect-cli.log', 'wb'),
        timeout=2)


def test_cli(server, client, editor):
    # ls
    client.expect(r'nete .*> ', timeout=2)
    client.sendline('ls')

    # new
    client.expect(r'nete .*> ', timeout=2)
    editor.set_content('Title: abc\n\nFOO')
    client.sendline('new')
    client.expect('Enter title.*: ')
    client.sendline('abc')
    client.expect('Created note with id (.*)')
    note_id = client.match[1].split()[0]

    # cat
    client.expect(r'nete .*> ', timeout=2)
    client.sendline('cat {}'.format(note_id.decode('utf-8')))
    client.expect('.*FOO')

    # edit
    client.expect(r'nete .*> ', timeout=2)
    editor.set_content('Title: abc\n\nBAR')
    client.sendline('edit {}'.format(note_id.decode('utf-8')))

    client.expect(r'nete .*> ', timeout=2)
    client.sendline('cat {}'.format(note_id.decode('utf-8')))
    client.expect('.*BAR')

    # exit
    client.expect(r'nete .*> ', timeout=2)
    client.sendline('exit')
    client.expect(pexpect.EOF, timeout=2)
