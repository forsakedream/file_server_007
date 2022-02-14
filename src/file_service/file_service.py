from typing import Optional, Tuple
from abc import ABCMeta, abstractmethod


class FileService(metaclass=ABCMeta):

    @abstractmethod
    def read(self, filename: str) -> Optional[str]:
        raise Exception("Not implemented")

    @abstractmethod
    def create(self, data: str) -> Tuple[str, Optional[str]]:
        raise Exception("Not implemented")

    @abstractmethod
    def ls(self) -> Optional[list]:
        raise Exception("Not implemented")

    @abstractmethod
    def cd(self, directory: str) -> Optional[bool]:
        raise Exception("Not implemented")

    @abstractmethod
    def remove(self, filename: str) -> Optional[bool]:
        raise Exception("Not implemented")

    @abstractmethod
    def read_metadata(self, filename: str) -> Optional[tuple]:
        raise Exception("Not implemented")

