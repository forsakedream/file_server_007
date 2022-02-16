from src.file_service import RawFileService, SignedFileService, EncryptedFileService
from src.config import Config


class ConsoleApp:
    def __init__(self, directory):
        self.raw_file_service = RawFileService(directory)
        self.file_service = self.raw_file_service
        if Config().is_encrypted():
            self.file_service = EncryptedFileService(self.file_service)
        if Config().is_signed():
            self.file_service = SignedFileService(self.file_service)

    def read(self):
        filename = input('Enter file name: ')
        try:
            data = self.file_service.read(filename)
            print(f"Reading file: {filename}")
            print(data)
        except Exception as e:
            print(e)

    def delete(self):
        filename = input('Enter file name: ')
        try:
            self.file_service.remove(filename)
            print(f"Delete file: {filename}")
        except Exception as e:
            print(e)

    def ls(self):
        print("list_dir")
        print(self.file_service.ls())

    def cd(self):
        directory = input("Enter dir name: ")
        try:
            self.file_service.cd(directory)
            print(f"Change dir: {directory}")
        except Exception as e:
            print(e)

    def create(self):
        content = input("Enter file content: ")
        filename = self.file_service.create(content)
        print(f"Creating file {filename} with content: \n{content}")

    def get_permissions(self):
        filename = input('Enter file name: ')
        try:
            permissions = self.file_service.get_permissions(filename)
            print(f'Permissions: {permissions}')
        except Exception as e:
            print(e)

    def set_permissions(self):
        filename = input('Enter file name: ')
        try:
            permissions = int(input("Enter UNIX permissions in oct format: "))
            self.file_service.set_permissions(filename, permissions)
            print(f'Setting {permissions} to filename {filename}')
        except Exception as e:
            print(e)

    def get_metadata(self):
        filename = input('Enter file name: ')
        try:
            result = self.file_service.read_metadata(filename)
            creation_date, modification_date, filesize = result
            print(f'Creation date: {creation_date}\n'
                  f'Modification date: {modification_date}\n'
                  f'File size: {filesize} Bytes')
        except Exception as e:
            print(e)