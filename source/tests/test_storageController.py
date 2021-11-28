from source.storageController import *


class TestFileController:
    def test_combo(self):
        storage_1 = StorageController.create_storage("kek")
        storage_1.write("1", "11")
        storage_1.write("2", "1111111")
        storage_2 = StorageController("kek")
        assert "11" == (storage_2.read("1"))
        assert "11" == (storage_1.read("1"))
        assert "1111111" == (storage_1.read("2"))
        storage_1.delete_key("2")
        storage_1.write("2", "2" * 3000)
        assert "2" * 3000 == storage_1.read("2")
        assert list(storage_1).__contains__("2")
        assert list(storage_1).__contains__("1")
        storage_1.delete_source()
