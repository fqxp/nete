from nete.backend.storage.filesystem import FilesystemStorage
from nete.backend.storage.exceptions import NotFound
import datetime
import pytest
import tempfile


class TestFilesystemStorage:

    @pytest.fixture
    def storage(self):
        storage = FilesystemStorage()
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage.open(tmp_dir)
            try:
                yield storage
            finally:
                storage.close()

    @pytest.fixture
    def new_note(self):
        return {
            'title': 'TITLE',
            'text': 'TEXT',
        }

    @pytest.mark.asyncio
    @pytest.mark.freeze_time
    async def test_list(self, storage, new_note):
        assert await storage.list() == []

        note = await storage.write(new_note)

        result = await storage.list()

        assert len(result) == 1
        assert result[0]['id'] == note['id']
        assert result[0]['title'] == note['title']
        assert result[0]['updated_at'] == datetime.datetime.utcnow()

    @pytest.mark.asyncio
    async def test_read_returns_note(self, storage, new_note):
        created_note = await storage.write(new_note)

        result = await storage.read(created_note['id'])

        assert result == created_note

    @pytest.mark.asyncio
    async def test_read_raises_NotFound_when_id_not_found(self, storage, new_note):
        with pytest.raises(NotFound):
            result = await storage.read('NON-EXISTING ID')

    @pytest.mark.asyncio
    @pytest.mark.freeze_time
    async def test_write_creates_and_returns_note(self, storage,  new_note):
        result = await storage.write(new_note)

        assert result['id'] is not None
        assert result['created_at'] == datetime.datetime.utcnow()
        assert result['updated_at'] == datetime.datetime.utcnow()
        assert result['title'] == 'TITLE'
        assert result['text'] == 'TEXT'

    @pytest.mark.asyncio
    async def test_write_writes_note_that_can_be_read(self, storage, new_note):
        result = await storage.write(new_note)

        note = await storage.read(result['id'])
        assert result['title'] == 'TITLE'

    @pytest.mark.freeze_time
    @pytest.mark.asyncio
    async def test_write_updates_existing_note(self, storage, new_note):
        new_note['created_at'] = datetime.datetime(2017, 1, 1)
        note = await storage.write(new_note)

        note['title'] = 'NEW TITLE'
        note['text'] = 'NEW TEXT'
        await storage.write(note)

        updated_note = await storage.read(note['id'])
        assert updated_note['created_at'] == datetime.datetime(2017, 1, 1)
        assert updated_note['updated_at'] == datetime.datetime.utcnow()
        assert updated_note['title'] == 'NEW TITLE'
        assert updated_note['text'] == 'NEW TEXT'

    @pytest.mark.asyncio
    async def test_delete_removes_note(self, storage, new_note):
        note = await storage.write(new_note)

        await storage.delete(note['id'])

        with pytest.raises(NotFound):
            await storage.read(note['id'])

    @pytest.mark.asyncio
    async def test_delete_raises_NotFound_if_note_doesnt_exist(self, storage, new_note):
        with pytest.raises(NotFound):
            await storage.delete('NON-EXISTING ID')
