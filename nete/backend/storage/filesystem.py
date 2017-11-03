from nete.util.json_util import default_serialize
from .exceptions import NotFound
from concurrent.futures import ThreadPoolExecutor
import asyncio
import datetime
import functools
import glob
import json
import logging
import os.path
import uuid


logger = logging.getLogger(__name__)


class FilesystemStorage:

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.executor = ThreadPoolExecutor()

    async def list(self):
        note_list = []
        for filename in glob.glob(os.path.join(self.base_dir, '*.nete')):
            note = await self._read_file(filename)
            note_list.append(
                {
                    'id': note['id'],
                    'title': note['title'],
                    'updated_at': note.get('updated_at'),
                })

        return note_list

    async def read(self, id):
        return await self._read_file(self._filename(id))

    async def write(self, note):
        now = datetime.datetime.utcnow()
        if note.get('id') is None:
            note['id'] = str(uuid.uuid4())
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
                data = await loop.run_in_executor(self.executor, json.load, fp)
                return data
        except FileNotFoundError:
            raise NotFound()

    def _filename(self, id):
        return os.path.join(self.base_dir, '{}.nete'.format(id))
