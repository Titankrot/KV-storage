from source.fileController import *
import pytest
import os

TEST_FILESTORAGE = "test_folder"
PATH = os.path.join(TEST_FILESTORAGE)
TEST_FILENAME = "test"


class TestFileController:
    def _init_file_controller(self):
        if not os.path.isdir(TEST_FILESTORAGE):
            os.mkdir(TEST_FILESTORAGE)
        return FileController(TEST_FILENAME, TEST_FILESTORAGE)

    def test_one_data(self):
        f = self._init_file_controller()
        key = "key"
        value = "value"
        bytes_value = str.encode(value)
        f.write_data(key, bytes_value)
        assert value == f.read_by_key(key).decode()
        f.delete_source()

    def test_more_data(self):
        f = self._init_file_controller()
        emptys = FILE_SIZE
        for i in range(5):
            value = str.encode("a" * i)
            f.write_data(str(i), value)
            emptys -= len(value)
            assert emptys == f.empty_space
        for i in range(5):
            value = str.encode("a" * i)
            assert "a" * i == f.read_by_key(str(i)).decode()
            f.delete_key(str(i))
            emptys += len(value)
            assert emptys == f.empty_space
        f.delete_source()

    def test_defragmentate(self):
        f = self._init_file_controller()
        f.write_data("1", bytes([1]*256))
        f.write_data("2", bytes([2]*256))
        f.write_data("3", bytes([3]*256))
        f.delete_key("2")
        f.write_data("4", bytes([4]*512))
        assert bytes([4]*512) == f.read_by_key("4")
        assert bytes([3]*256) == f.read_by_key("3")
        assert bytes([1]*256) == f.read_by_key("1")
        f.delete_source()
