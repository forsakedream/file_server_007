from .file_service import FileService
from typing import Tuple
from src import utils
from src.crypto import Encryption


class EncryptedFileService(FileService):
    def __init__(self, wrapped_file_service):
        self.wrapped_file_service = wrapped_file_service

    def read(self, filename: str) -> str:
        encryptor = Encryption.get_encryptor(filename)
        key_file_name = encryptor.key_name(filename)
        with open(key_file_name, "rb") as f:
            key = f.read()
        with open(filename, "rb") as file:
            encrypted_data = [file.read(x) for x in (16, 16, -1)]
        decrypted_data = encryptor.decrypt(encrypted_data, key)
        return decrypted_data

    def create(self, data: str):
        encryptor = Encryption.get_default_encryptor()
        encrypted_data, key = encryptor.encrypt(data)
        filename = utils.generate_name(10)
        with open(filename, "wb") as file:
            [file.write(x) for x in encrypted_data]
        key_file_name = encryptor.key_name(filename)
        with open(key_file_name, "wb") as file:
            file.write(key)
        return filename, key_file_name

    def ls(self):
        return self.wrapped_file_service.ls()

    def cd(self, dir: str) -> None:
        return self.wrapped_file_service.cd(dir)

    def remove(self, filename: str) -> None:
        self.wrapped_file_service.remove(filename)
        key_name = Encryption.get_encryptor(filename).key_name(filename)
        self.wrapped_file_service.remove(key_name)

    def read_metadata(self, filename: str) -> Tuple[int, int, int]:
        return self.wrapped_file_service.read_metadata(filename)