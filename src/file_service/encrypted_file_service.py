from .file_service import FileService
from src import utils
from src.crypto import Encryption


class EncryptedFileService(FileService):
    def __init__(self, wrapped_file_service):
        self.wrapped_file_service = wrapped_file_service
        self.workdir = wrapped_file_service.workdir

    def read(self, filename):
        encryptor = Encryption.get_encryptor(filename)
        key_file_name = encryptor.key_name(filename)
        with open(key_file_name, "rb") as f:
            key = f.read()
        with open(filename, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = encryptor.decrypt(encrypted_data, key)
        return decrypted_data

    def create(self, data):
        encryptor = Encryption.get_default_encryptor()
        encrypted_data, key = encryptor.encrypt(data)
        filename = utils.generate_name(10)
        with open(filename, "wb") as file:
            file.write(encrypted_data)
        key_file_name = encryptor.key_name(filename)
        with open(key_file_name, "wb") as file:
            file.write(key)
        return filename

    def ls(self):
        return self.wrapped_file_service.ls()

    def cd(self, dir):
        return self.wrapped_file_service.cd(dir)

    def remove(self, filename):
        self.wrapped_file_service.remove(filename)
        key_name = Encryption.get_encryptor(filename).key_name(filename)
        self.wrapped_file_service.remove(key_name)

    def read_metadata(self, filename):
        return self.wrapped_file_service.read_metadata(filename)

    def get_permissions(self, filename):
        return self.wrapped_file_service.get_permissions(filename)

    def set_permissions(self, filename, permissions):
        return self.wrapped_file_service.get_permissions(filename, permissions)
