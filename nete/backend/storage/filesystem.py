from nete.util.json_util import default_serialize
from nete.util.lockable import Lockable
from .exceptions import NotFound
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import asyncio
import contextlib
import datetime
import dateutil.parser
import functools
import json
import logging
import os
import os.path
import uuid


logger = logging.getLogger(__name__)


class FilesystemStorage(Lockable):

    def __init__(self):
        self.executor = ThreadPoolExecutor()

    @contextlib.contextmanager
    def open(self, base_dir):
        self.base_dir = Path(base_dir)

        try:
            self.lock(self.base_dir / '.lock')
            yield
        finally:
            self.unlock()

    @Lockable.ensure_lock
    async def list(self):
        note_list = []
        for filename in self.base_dir.glob('*.nete'):
            note = await self._read_file(filename)
            note_list.append(
                {
                    'id': note['id'],
                    'title': note['title'],
                    'updated_at': note.get('updated_at'),
                })

        return note_list

    @Lockable.ensure_lock
    async def read(self, id):
        return await self._read_file(self._filename(id))

    @Lockable.ensure_lock
    async def write(self, note):
        now = datetime.datetime.utcnow()
        if note.get('id') is None:
            note['id'] = str(uuid.uuid4())
        if note.get('created_at') is None:
            note['created_at'] = now
        note['updated_at'] = now

        filename = self._filename(note['id'])
        with open(filename, 'w') as fp:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
              self.executor,
              functools.partial(json.dump, note, fp,
                                default=default_serialize))

        return note

    @Lockable.ensure_lock
    async def delete(self, note_id):
        filename = self._filename(note_id)
        if not os.path.exists(filename):
            raise NotFound()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, os.unlink, filename)

    async def _read_file(self, filename):
        logger.debug('opening file {} for reading'.format(filename))
        try:
            with open(filename) as fp:
                loop = asyncio.get_event_loop()
                note = await loop.run_in_executor(self.executor, json.load, fp)
                if 'created_at' in note:
                    try:
                        note['created_at'] = dateutil.parser.parse(note['created_at'])
                    except TypeError:
                        pass
                if 'updated_at' in note:
                    try:
                        note['updated_at'] = dateutil.parser.parse(note['updated_at'])
                    except TypeError:
                        pass
                return note
        except FileNotFoundError:
            raise NotFound()

    def _filename(self, id):
        return self.base_dir / '{}.nete'.format(id)
