import subprocess


class pytest_io:
    def __init__(self, cmd, env={}, timeout=5):
        self.cmd = cmd
        self.env = env
        self.timeout = timeout

    def __call__(self, *args):
        self.proc = subprocess.Popen(
            [self.cmd, *args],
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )
        return self._readouterr()

    def _readouterr(self):
        try:
            out, err = self.proc.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            out, err = self.proc.communicate(timeout=self.timeout)

        return out.decode('utf-8'), err.decode('utf-8')

    def returncode(self):
        return self.proc.returncode
