from .nete_client import NeteClient
import logging
import uuid

logger = logging.getLogger(__name__)


class Synchronizer:

    def __init__(self, storage, sync_url):
        self.storage = storage
        self.sync_url = sync_url

    async def synchronize(self):
        logger.info('Starting sync')

        status = self.storage.load_status()

        async with NeteClient(self.sync_url) as client:
            local_revisions = {
                note.id: note.revision_id
                for note in await self.storage.list()
            }
            remote_revisions = {
                note.id: note.revision_id
                for note in await client.list_notes()
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
                is_changed_here = (local_revisions[note_id] != status[note_id])
                is_changed_there = (remote_revisions[note_id] != status[note_id])
                if (is_changed_here and not is_changed_there):
                    updated_here.add(note_id)
                elif (not is_changed_here and is_changed_there):
                    updated_there.add(note_id)
                elif (is_changed_here and is_changed_there):
                    updated_here_and_there.add(note_id)

            logger.debug(
                'Diff: '
                '{} created here, '
                '{} created there, '
                '{} updated here, '
                '{} updated there, '
                '{} updated here and there'.format(
                    len(created_here),
                    len(created_there),
                    len(updated_here),
                    len(updated_there),
                    len(updated_here_and_there)))

            conflict_copy_ids = await self._create_conflict_copies(
                updated_here_and_there)

            await self._create_notes(
                client,
                [note_id for note_id in created_here | conflict_copy_ids])
            await self._update_notes(
                client,
                [(note_id, status[note_id])
                 for note_id in updated_here])
            await self._pull_notes(
                client,
                created_there | updated_there | updated_here_and_there)

        await self.storage.update_status()

    async def _create_notes(self, client, note_ids):
        for note_id in note_ids:
            logger.debug('Creating note {}'.format(note_id))
            note = await self.storage.read(note_id)
            await client.create_note(note)

    async def _update_notes(self, client, note_ids_and_revision_ids):
        for (note_id, old_revision_id) in note_ids_and_revision_ids:
            note = await self.storage.read(note_id)
            logger.debug('Updating note {} (rev id: {}, old rev id: {})'
                         .format(note.id, note.revision_id, old_revision_id))
            await client.update_note(note, old_revision_id)

    async def _pull_notes(self, client, note_ids):
        for note_id in note_ids:
            logger.debug('Pulling note {}'.format(note_id))
            note = await client.get_note(note_id)
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
