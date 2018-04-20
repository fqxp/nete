from nete.common.schemas.note_schema import NoteSchema
from nete.common.schemas.note_index_schema import NoteIndexSchema
from urllib.parse import urljoin
import urllib.parse
import aiohttp
import logging

logger = logging.getLogger(__name__)
note_index_schema = NoteIndexSchema()
note_schema = NoteSchema()


class Synchronizer:

    def __init__(self, storage, sync_url):
        self.storage = storage
        self._prepare_url(sync_url)

    def _prepare_url(self, sync_url):
        parsed_url = urllib.parse.urlparse(sync_url)
        if parsed_url.scheme == 'local':
            # the unix domain connector still expects a valid
            # hostname in the URL
            self.base_url = 'http://localhost'
            self.connector = aiohttp.UnixConnector(parsed_url.path)
        else:
            self.base_url = sync_url
            self.connector = aiohttp.TCPConnector()

    async def synchronize(self):
        logger.info('Starting sync')
        async with aiohttp.ClientSession(connector=self.connector) as session:
            remote_notes = await self._list_remote_notes(session)
            remote_note_ids = {note.id for note in remote_notes}
            local_notes = await self.storage.list()
            local_note_ids = {note.id for note in local_notes}

            not_here = remote_note_ids - local_note_ids
            not_there = local_note_ids - remote_note_ids
            # both = local_note_ids & remote_note_ids

            await self._push_notes(
                session,
                [note
                 for note in local_notes
                 if note.id in not_there])
            await self._pull_notes(
                session,
                not_here)

    async def _list_remote_notes(self, session):
        index_url = urljoin(self.base_url, '/notes')
        response = await session.get(index_url)
        return note_index_schema.loads(
            await response.text(),
            many=True)

    async def _push_notes(self, session, notes):
        url = urljoin(self.base_url, '/notes')
        for note in notes:
            logger.debug('Pushing note {}'.format(note.id))
            response = await session.post(
                url,
                headers={
                    'content-type': 'application/json',
                },
                data=note_schema.dumps(note))
            if response.status != 201:
                logger.error('Error during sync (push {}):\n{}'.format(
                    note.id, await response.text()))

    async def _pull_notes(self, session, note_ids):
        for note_id in note_ids:
            logger.debug('Pulling note {}'.format(note_id))
            url = urljoin(self.base_url, '/notes/{}'.format(str(note_id)))
            response = await session.get(url)
            note = note_schema.loads(await response.text())
            await self.storage.write(note)
