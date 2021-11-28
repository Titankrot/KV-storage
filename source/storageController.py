import shutil
import os
import json
import hashlib
from source.fileController import FileController, JSON_EXTENTION, FILE_SIZE

FILES_COUNT = 10
CONF = "conf.json"
CONT_DIR = "containers"
KEYS_JSON_DIRS = "KEYS"


class StorageController:
    def __init__(self, directory):
        self._cont_dir = os.path.join(directory, CONT_DIR)
        self._key_json_dir = os.path.join(directory, KEYS_JSON_DIRS)
        self._conf_file = os.path.join(directory, CONF)
        with open(self._conf_file, 'r') as conf:
            data = json.load(conf)
        self._content_files = data["conts"]
        self._keys_jsons = data["keys_jsons"]
        self._directory = directory

    @staticmethod
    def create_storage(directory):
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)
        with open(os.path.join(directory, CONF), 'w') as conf:
            data = {"conts": {}, "keys_jsons": []}
            json.dump(data, conf)
        os.mkdir(os.path.join(directory, CONT_DIR))
        os.mkdir(os.path.join(directory, KEYS_JSON_DIRS))
        return StorageController(directory)

    def _dump_in_conf(self):
        with open(self._conf_file, 'w') as conf:
            data = {"conts": self._content_files,
                    "keys_jsons": self._keys_jsons}
            json.dump(data, conf)

    def _get_filename(self, key: str):
        hash_from_key = hashlib.md5(key.encode())
        hash_from_key = int(hash_from_key.hexdigest(), 16) % FILES_COUNT
        return os.path.join(self._key_json_dir,
                            str(hash_from_key) + JSON_EXTENTION)

    def __contains__(self, key: str):
        path = self._get_filename(key)
        if not os.path.isfile(path):
            return False
        with open(path, 'r') as file:
            files_by_key = json.load(file)
        if key not in files_by_key:
            return False
        return True

    def read(self, key: str):
        if key not in self:
            return None
        path = self._get_filename(key)
        with open(path, 'r') as file:
            files_by_key = json.load(file)
        value = bytes()
        for filename in files_by_key[key]:
            value += FileController(filename, self._cont_dir).read_by_key(key)
        return value.decode()

    def _write_in_file(self, key: str, value: bytes, filename):
        file = FileController(filename, self._cont_dir)
        file.write_data(key, value)
        self._content_files[filename] = file.empty_space

        path = self._get_filename(key)
        if not os.path.isfile(path):
            with open(path, 'w') as file:
                files_by_key = {}
                json.dump(files_by_key, file)
            self._keys_jsons.append(path)
        with open(path, 'r') as file:
            files_by_key = json.load(file)
            if key not in files_by_key:
                files_by_key[key] = []
            files_by_key[key].append(filename)
        with open(path, 'w') as file:
            json.dump(files_by_key, file)
        self._dump_in_conf()

    def _write_in_new_file(self, key: str, value: bytes):
        name = str(len(self._content_files))
        for i in range(len(self._content_files)):
            if str(i) not in self._content_files:
                name = str(i)
                break

        self._write_in_file(key, value, name)

    def _write_small(self, key: str, value: bytes):
        if len(value) == FILE_SIZE:
            self._write_in_new_file(key, value)
            return
        for filename in self._content_files.keys():
            if self._content_files[filename] >= len(value):
                self._write_in_file(key, value, filename)
                return
        self._write_in_new_file(key, value)

    def write(self, key: str, value: str):
        if key in self:
            self.delete_key(key)
        value = value.encode()
        count = len(value) // FILE_SIZE
        index = 0
        for i in range(count):
            self._write_in_new_file(key, value[index:index + FILE_SIZE])
            index += FILE_SIZE
        self._write_small(key, value[index:])

    def delete_key(self, key):
        if key not in self:
            return None
        path = self._get_filename(key)
        need_to_delete = False
        with open(path, "r") as file:
            files_by_key = json.load(file)
            for filename in files_by_key[key]:
                file = FileController(filename, self._cont_dir)
                file.delete_key(key)
                if file.empty_space == FILE_SIZE:
                    file.delete_source()
                    self._content_files.pop(filename)
                else:
                    self._content_files[filename] = file.empty_space
            files_by_key.pop(key)
            if len(files_by_key) == 0:
                need_to_delete = True
        with open(path, "w") as file:
            json.dump(files_by_key, file)
        if need_to_delete:
            self._keys_jsons.remove(path)
            os.remove(path)
        self._dump_in_conf()

    def delete_source(self):
        shutil.rmtree(self._directory)

    def __iter__(self):
        for path in self._keys_jsons:
            with open(path, 'r') as file:
                data = json.load(file)
                for key in data:
                    yield key


if __name__ == '__main__':
    storage = StorageController.create_storage("kek")
    storage.write("1", "11")
    storage.write("2", "1111111")
    storage2 = StorageController("kek")
    print(storage2.read("1"))
    storage.delete_key("2")
    storage.write("2", "2"*3000)
    print(storage.read("2"))
    print(list(storage))
