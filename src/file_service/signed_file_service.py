from .file_service import FileService
from typing import Tuple
from src.crypto import Signature


class SignedFileService(FileService):
    def __init__(self, wrapped_file_service):
        self.wrapped_file_service = wrapped_file_service

    def read(self, filename: str) -> str:
        """
            Read signed file from disk and check content

            :param filename: name of file
            :return: file content, if file exists and not broken, else False
            """
        data = self.wrapped_file_service.read(filename)

        signer = Signature().get_signer(filename)
        with open(signer.sig_filename(filename), 'r') as sig_file:
            if str(signer(data)) == str(sig_file.read()):
                return data
            else:
                raise Exception("File is Broken")

    def create(self, content: str):
        """
        Create signed file with unique file name and desired content

        :param signer: md5, sha512
        :param content: content of created file
        :return: unique filename
        """
        filename = self.wrapped_file_service.create(content)
        signer = Signature().get_default_signer()
        sig_filename = signer.sig_filename(filename)
        sig_content = signer(content)
        with open(sig_filename, "w") as file:
            file.write(sig_content)
        return filename

    def ls(self):
        return self.wrapped_file_service.ls()

    def cd(self, directory: str):
        return self.wrapped_file_service.cd(directory)

    def remove(self, filename: str):
        self.wrapped_file_service.remove(filename)
        signer = Signature().get_signer(filename)
        sig_filename = signer.sig_filename(filename)
        self.wrapped_file_service.remove(sig_filename)

    def read_metadata(self, filename: str) -> Tuple[int, int, int]:
        return self.wrapped_file_service.read_metadata(filename)