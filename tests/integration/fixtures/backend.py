import contextlib
import subprocess
import sys
import time


@contextlib.contextmanager
def backend(config_filename, prefix='backend'):
    args = ['-c', config_filename]
    process = subprocess.Popen(
        ['nete-backend', *args],
        stdout=sys.stdout,
        stderr=subprocess.STDOUT)
    time.sleep(1)
    yield process

    process.terminate()
    try:
        process.wait()
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
