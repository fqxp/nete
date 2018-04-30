from .lockable import Lockable
from nete.backend.schemas import StatusItemSchema
from nete.backend.storage.exceptions import NotFound
from nete.common.schemas.note_schema import NoteSchema
from concurrent.futures import ThreadPoolExecutor
import asyncio
import glob
import logging
import os
import os.path


logger = logging.getLogger(__name__)


class FilesystemStorage(Lockable):

    STATUS_FILENAME = 'status.json'

    def __init__(self, base_dir):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.executor = ThreadPoolExecutor()

    def open(self):
        logger.info('Opening storage in directory {}'.format(self.base_dir))
        self.lock(os.path.join(self.base_dir, '.lock'))

    def close(self):
        self.unlock()

    @Lockable.ensure_lock
    async def list(self):
        note_list = []
        for filename in glob.glob(os.path.join(self.base_dir, '*.nete')):
            note = await self._read_file(filename)
            note_list.append(note)

        return note_list

    @Lockable.ensure_lock
    async def read(self, id):
        return await self._read_file(self._filename(id))

    @Lockable.ensure_lock
    async def write(self, note):
        filename = self._filename(note.id)
        logger.debug('Opening file {} for writing'.format(filename))
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

    # TODO: locking
    def load_status(self):
        if not os.path.exists(self._status_filename()):
            return {}

        with open(self._status_filename()) as f:
            status_items = StatusItemSchema().loads(f.read(), many=True)
            return {
                status_item['note_id']: status_item['revision_id']
                for status_item in status_items
            }

    @Lockable.ensure_lock
    async def update_status(self):
        status_items = [
            {
                'note_id': note.id,
                'revision_id': note.revision_id,
            } for note in await self.list()
        ]
        with open(self._status_filename(), 'w') as f:
            f.write(StatusItemSchema().dumps(status_items, many=True))

    async def _read_file(self, filename):
        logger.debug('Opening file {} for reading'.format(filename))
        note_schema = NoteSchema()
        try:
            note_data = open(filename).read()
            return note_schema.loads(note_data)
        except FileNotFoundError:
            raise NotFound()

    def _filename(self, note_id):
        return os.path.join(self.base_dir, '{!s}.nete'.format(note_id))

    def _status_filename(self):
        return os.path.join(self.base_dir, self.STATUS_FILENAME)
