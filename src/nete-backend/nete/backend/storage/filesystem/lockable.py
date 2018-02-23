import functools
import os
import os.path


class AlreadyLocked(Exception):
    pass


class NotLocked(Exception):
    pass


class Lockable:

    lock_filename = None

    def lock(self, lock_filename):
        self.lock_filename = lock_filename
        self.remove_stale_lockfile()
        if os.path.exists(self.lock_filename):
            raise AlreadyLocked('lockfile {} exists'
                                .format(self.lock_filename))

        with open(self.lock_filename, 'w') as fp:
            fp.write(str(os.getpid()))

    def unlock(self):
        if os.path.exists(self.lock_filename):
            os.unlink(self.lock_filename)
        self.lock_filename = None

    def is_locked(self):
        return self.lock_filename and os.path.exists(self.lock_filename)

    def ensure_lock(f):
        @functools.wraps(f)
        async def locked_f(self, *args, **kwargs):
            if not self.is_locked():
                raise NotLocked()
            return await f(self, *args, **kwargs)

        return locked_f

    def remove_stale_lockfile(self):
        try:
            pid = int(open(self.lock_filename, 'r').read())
            if not self._is_process_running(pid):
                os.unlink(self.lock_filename)
        except (FileNotFoundError, ValueError):
            pass

    def _is_process_running(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
