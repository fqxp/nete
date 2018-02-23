import os
import tempfile


class Editor:
    def __enter__(self):
        self.content_fp = tempfile.NamedTemporaryFile()
        self.previous_content_fp = tempfile.NamedTemporaryFile()

        self._generate_cmd()

        return self

    def __exit__(self, *args):
        os.unlink(self.cmd_name)
        self.content_fp.close()
        self.previous_content_fp.close()

    def env(self):
        return {'EDITOR': self.cmd_name}

    def get_content(self):
        self.previous_content_fp.seek(0)
        return self.previous_content_fp.read().decode('utf-8')

    def set_content(self, content):
        self.content_fp.seek(0)
        self.content_fp.write(content.encode('utf-8'))
        self.content_fp.truncate()
        self.content_fp.flush()

    def _generate_cmd(self):
        with tempfile.NamedTemporaryFile(delete=False) as cmd_fp:
            self.cmd_name = cmd_fp.name
            cmd_fp.write(
                '#!/bin/bash\n'
                'cat $1 >{previous_content_file}\n'
                'if [ -n "$(cat {content_file})" ] ; then\n'
                '  cat {content_file} >$1\n'
                'fi'
                .format(
                    previous_content_file=self.previous_content_fp.name,
                    content_file=self.content_fp.name)
                .encode('utf-8'))
            cmd_fp.close()
            os.chmod(self.cmd_name, 0o755)
