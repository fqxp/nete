from .lockable import Lockable
from nete.backend.storage.exceptions import NotFound
from nete.schemas.note_schema import NoteSchema
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import asyncio
import logging
import os
import os.path


logger = logging.getLogger(__name__)


class FilesystemStorage(Lockable):

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.executor = ThreadPoolExecutor()

    def open(self):
        self.lock(self.base_dir / '.lock')

    def close(self):
        self.unlock()

    @Lockable.ensure_lock
    async def list(self):
        note_list = []
        for filename in self.base_dir.glob('*.nete'):
            note = await self._read_file(filename)
            note_list.append(note)

        return note_list

    @Lockable.ensure_lock
    async def read(self, id):
        return await self._read_file(self._filename(id))

    @Lockable.ensure_lock
    async def write(self, note):
        filename = self._filename(str(note.id))
        note_schema = NoteSchema()
        with open(filename, 'w') as fp:
            fp.write(note_schema.dumps(note))

    @Lockable.ensure_lock
    async def delete(self, note_id):
        filename = self._filename(note_id)
        if not os.path.exists(filename):
            raise NotFound()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, os.unlink, filename)

    async def _read_file(self, filename):
        logger.debug('opening file {} for reading'.format(filename))
        note_schema = NoteSchema()
        try:
            note_data = open(filename).read()
            return note_schema.loads(note_data)
        except FileNotFoundError:
            raise NotFound()

    def _filename(self, id):
        return self.base_dir / '{}.nete'.format(id)
