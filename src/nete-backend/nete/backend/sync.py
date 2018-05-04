from nete.common.schemas.note_index_schema import NoteIndexSchema
from nete.common.schemas.note_schema import NoteSchema
from urllib.parse import urljoin
import aiohttp
import logging
import uuid

logger = logging.getLogger(__name__)
note_index_schema = NoteIndexSchema()
note_schema = NoteSchema()


class Synchronizer:

    def __init__(self, storage, sync_url):
        self.storage = storage
        self._prepare_url(sync_url)

    def _prepare_url(self, sync_url):
        if sync_url.is_socket_url():
            # the unix domain connector expects a valid
            # hostname in the URL
            self.base_url = 'http://localhost'
            self.connector = aiohttp.UnixConnector(sync_url.socket_path)
        else:
            self.base_url = sync_url
            self.connector = aiohttp.TCPConnector()

    async def synchronize(self):
        logger.info('Starting sync')

        status = self.storage.load_status()

        async with aiohttp.ClientSession(connector=self.connector) as session:
            local_revisions = {
                note.id: note.revision_id
                for note in await self.storage.list()
            }
            remote_revisions = {
                note.id: note.revision_id
                for note in await self._list_remote_notes(session)
            }

            created_there = (
                remote_revisions.keys() -
                local_revisions.keys())
            created_here = (
                local_revisions.keys() -
                remote_revisions.keys())

            both = (
                local_revisions.keys() &
                remote_revisions.keys())

            updated_here = set()
            updated_there = set()
            updated_here_and_there = set()
            for note_id in both:
                if (local_revisions[note_id] != status[note_id] and
                    remote_revisions[note_id] == status[note_id]):
                    updated_here.add(note_id)
                elif (local_revisions[note_id] == status[note_id] and
                      remote_revisions[note_id] != status[note_id]):
                    updated_there.add(note_id)
                elif (local_revisions[note_id] != status[note_id] and
                      remote_revisions[note_id] != status[note_id]):
                    updated_here_and_there.add(note_id)

            conflict_copy_ids = await self._create_conflict_copies(
                updated_here_and_there)

            await self._create_notes(
                session,
                [note_id for note_id in created_here | conflict_copy_ids])
            await self._update_notes(
                session,
                [(note_id, status[note_id])
                 for note_id in updated_here])
            await self._pull_notes(
                session,
                created_there | updated_there | updated_here_and_there)

        await self.storage.update_status()

    async def _list_remote_notes(self, session):
        index_url = urljoin(self.base_url, '/notes')
        response = await session.get(index_url)
        return note_index_schema.loads(
            await response.text(),
            many=True)

    async def _create_notes(self, session, note_ids):
        url = urljoin(self.base_url, '/notes')
        for note_id in note_ids:
            logger.debug('Creating note {}'.format(note_id))
            note = await self.storage.read(note_id)
            response = await session.post(
                url,
                headers={
                    'content-type': 'application/json',
                },
                data=note_schema.dumps(note))
            if response.status != 201:
                logger.error('Error during sync (create {}):\n{}'.format(
                    note.id, await response.text()))

    async def _update_notes(self, session, note_ids_and_revision_ids):
        for (note_id, old_revision_id) in note_ids_and_revision_ids:
            url = urljoin(self.base_url, '/notes/{}'.format(note_id))
            note = await self.storage.read(note_id)
            logger.debug('Updating note {} (rev id: {}, old rev id: {})'
                         .format(note.id, note.revision_id, old_revision_id))
            response = await session.put(
                url,
                headers={
                    'content-type': 'application/json',
                    'if-match': str(old_revision_id),
                },
                data=note_schema.dumps(note))
            if response.status != 200:
                logger.error('Error during sync (update {}):\n{}'.format(
                    note.id, await response.text()))

    async def _pull_notes(self, session, note_ids):
        for note_id in note_ids:
            logger.debug('Pulling note {}'.format(note_id))
            url = urljoin(self.base_url, '/notes/{}'.format(str(note_id)))
            response = await session.get(url)
            note = note_schema.loads(await response.text())
            await self.storage.write(note)
            logger.debug('write note: {!r}'.format(note))

    async def _create_conflict_copies(self, note_ids):
        conflict_copy_ids = set()
        for note_id in note_ids:
            note = await self.storage.read(note_id)
            note.id = uuid.uuid4()
            note.revision_id = uuid.uuid4()
            await self.storage.write(note)
            conflict_copy_ids.add(note.id)

        return conflict_copy_ids
