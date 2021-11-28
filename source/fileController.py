import json
import os

CONTAINER_EXTENTION = ".cont"
JSON_EXTENTION = ".json"
FILE_SIZE = 1024


class FileController:
    def __init__(self, filename: str, path: str):
        self._filename = os.path.join(path, filename + CONTAINER_EXTENTION)
        self._file_json = os.path.join(path, filename + JSON_EXTENTION)
        if not os.path.isfile(self._filename):
            self._create_files()
        else:
            self._load_in_conf()

    def _dump_in_conf(self):
        with open(self._file_json, 'w') as conf:
            data = {"t": self._translation_table,
                    "e": self._emptys_table,
                    "s": self._empty_space}
            json.dump(data, conf)

    def _load_in_conf(self):
        with open(self._file_json, 'r') as conf:
            data = json.load(conf)
        self._translation_table = data["t"]
        self._emptys_table = {int(k): w for k, w in data["e"].items()}
        self._empty_space = data["s"]

    def _create_files(self):
        with open(self._filename, 'wb') as file:
            file.write(bytes(FILE_SIZE))
        self._emptys_table = {0: FILE_SIZE}
        self._translation_table = {}
        self._empty_space = FILE_SIZE
        self._dump_in_conf()

    def read_by_key(self, key: str):
        if key not in self._translation_table.keys():
            raise ValueError("key not in file")
        pos, size = self._translation_table[key]
        with open(self._filename, "rb") as file:
            file.seek(pos)
            data = file.read(size)
        return data

    @property
    def empty_space(self):
        return self._empty_space

    def _write(self, key, value, index):
        with open(self._filename, 'rb+') as file:
            file.seek(index)
            file.write(value)
        self._translation_table[key] = (index, len(value))
        empty_length = self._emptys_table[index]
        self._emptys_table.pop(index)
        if empty_length != len(value):
            new_index = index + len(value)
            new_empty_length = empty_length - len(value)
            self._emptys_table[new_index] = new_empty_length
        self._empty_space -= len(value)
        self._dump_in_conf()

    def _defragmentate(self):
        data = bytes()
        new_translation_table = {}
        with open(self._filename, "rb+") as file:
            for key in self._translation_table:
                pos, size = self._translation_table[key]
                file.seek(pos)
                value = file.read(size)
                new_translation_table[key] = (len(data), size)
                data += value
            self._emptys_table = {len(data): self._empty_space}
            data += bytes(self._empty_space)
            file.seek(0)
            file.write(data)
            file.truncate()
        self._translation_table = new_translation_table
        self._dump_in_conf()

    def write_data(self, key: str, value: bytes):
        if len(value) > self._empty_space:
            raise ValueError("Value is too large")
        for (index, length) in self._emptys_table.items():
            if length >= len(value):
                self._write(key, value, index)
                return
        self._defragmentate()
        self.write_data(key, value)

    def delete_key(self, key):
        (pos, size) = self._translation_table.pop(key)
        self._emptys_table[pos] = size
        self._empty_space += size
        self._dump_in_conf()

    def delete_source(self):
        os.remove(self._filename)
        os.remove(self._file_json)
