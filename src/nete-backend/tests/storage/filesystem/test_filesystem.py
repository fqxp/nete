from nete.backend.storage.filesystem import FilesystemStorage
from nete.backend.storage.exceptions import NotFound
from nete.common.schemas.note_schema import NoteSchema
import datetime
import pytest
import pytz
import tempfile


class TestFilesystemStorage:

    @pytest.fixture
    def storage(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage = FilesystemStorage(tmp_dir)
            storage.open()
            try:
                yield storage
            finally:
                storage.close()

    @pytest.fixture
    def new_note(self):
        return NoteSchema().load({
            'title': 'TITLE',
            'text': 'TEXT',
        })

    @pytest.mark.asyncio
    @pytest.mark.freeze_time
    async def test_list(self, storage, new_note):
        assert await storage.list() == []

        await storage.write(new_note)

        result = await storage.list()

        assert len(result) == 1
        assert result[0].id == new_note.id
        assert result[0].title == new_note.title
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        assert result[0].created_at == now
        assert result[0].updated_at == now

    @pytest.mark.asyncio
    async def test_read_raises_NotFound_when_id_not_found(self, storage,
                                                          new_note):
        with pytest.raises(NotFound):
            await storage.read('NON-EXISTING ID')

    @pytest.mark.asyncio
    @pytest.mark.freeze_time
    async def test_write_creates_and_returns_note(self, storage,  new_note):
        await storage.write(new_note)

        note = await storage.read(new_note.id)
        assert note.id is not None
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        assert note.created_at == now
        assert note.updated_at == now
        assert note.title == 'TITLE'
        assert note.text == 'TEXT'

    @pytest.mark.asyncio
    async def test_write_writes_note_that_can_be_read(self, storage, new_note):
        await storage.write(new_note)

        note = await storage.read(new_note.id)
        assert note.title == 'TITLE'

    @pytest.mark.freeze_time
    @pytest.mark.asyncio
    async def test_write_updates_existing_note(self, storage, new_note):
        new_note.created_at = datetime.datetime(2017, 1, 1)
        await storage.write(new_note)

        new_note.title = 'NEW TITLE'
        new_note.text = 'NEW TEXT'
        await storage.write(new_note)

        updated_note = await storage.read(new_note.id)
        assert (updated_note.created_at ==
                datetime.datetime(2017, 1, 1, tzinfo=pytz.UTC))
        assert (updated_note.updated_at ==
                datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        assert updated_note.title == 'NEW TITLE'
        assert updated_note.text == 'NEW TEXT'

    @pytest.mark.asyncio
    async def test_delete_removes_note(self, storage, new_note):
        await storage.write(new_note)

        await storage.delete(new_note.id)

        with pytest.raises(NotFound):
            await storage.read(new_note.id)

    @pytest.mark.asyncio
    async def test_delete_raises_NotFound_if_note_doesnt_exist(self, storage,
                                                               new_note):
        with pytest.raises(NotFound):
            await storage.delete('NON-EXISTING ID')
