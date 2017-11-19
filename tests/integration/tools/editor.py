import os
import tempfile


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

