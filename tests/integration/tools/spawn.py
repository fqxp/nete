import pexpect


class spawn(pexpect.spawn):

    def __init__(self, *args, **kwargs):
        self.logfile = CaptureFile()
        super().__init__(
            *args,
            echo=False,
            logfile=self.logfile,
            **kwargs)

    def sendline(self, s):
        self.logfile.reset()
        super().sendline(s)

    def assertExpect(self, s):
        try:
            super().expect(s)
        except (pexpect.EOF, pexpect.TIMEOUT):
            raise AssertionError(
                '»{}« does not match »{}«'.format(
                    self.logfile.output.decode('utf-8'), s))


class CaptureFile:
    def __init__(self):
        self.reset()

    def write(self, s):
        self.output += s

    def flush(self):
        pass

    def reset(self):
        self.output = b''
