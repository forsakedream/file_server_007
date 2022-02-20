from .file_service import FileService
import os
import logging
from src import utils
from datetime import datetime as dt
from typing import Optional


def _to_dt(time: float) -> str:
    return dt.utcfromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")


class RawFileService(FileService):
    def __init__(self, workdir="."):
        self.workdir = workdir
        os.chdir(self.workdir)

    def read(self, filename):
        """
        Read file from disk by filename

        :param filename: name of file
        :return: file content, if file exists, else raise exception
        """
        if os.path.isfile(filename) and (not os.path.isdir(filename)):
            logging.debug(f"Opening: {filename}")
            with open(filename, 'r') as file:
                return file.read()
        else:
            raise ValueError(f"Not Found: {filename}")

    def create(self, content):
        """
        Create file with unique file name and desired content

        :param content: content of created file
        :return: unique filename
        """
        filename = utils.generate_name(10)
        logging.debug(f"Generated name: {filename}")
        with open(filename, "w") as file:
            file.write(content)
        return filename

    def ls(self):
        """
        Return list of files and directories in the current directory

        :return: list of files and directories in the current directory
        """
        logging.debug(f"Listing directories in current dir")
        return os.listdir()

    def cd(self, directory):
        """
        Change current directory

        :param directory: name of directory
        :return: True, if desired directory is valid, else False
        """
        if os.path.isdir(directory):
            self.workdir = directory
            logging.debug(f"Changing dir to: {directory}")
            os.chdir(directory)
            return True
        else:
            raise ValueError(f"Not Found: {directory}")

    def remove(self, filename):
        """
        Delete string by filename

        :param filename: name of file
        :return: True, if file deleted, else False
        """
        if os.path.isfile(filename) and (not os.path.isdir(filename)):
            logging.debug(f"Deleting: {filename}")
            os.remove(filename)
            return True
        else:
            raise ValueError(f"Not Found: {filename}")

    def read_metadata(self, filename):
        """
        Read file creation date, edit date, file size

        :param filename:
        :return tuple (create_date, modification_date, file size), file exists, else False
        """
        if os.path.isfile(filename) and (not os.path.isdir(filename)):
            stat = os.stat(filename)
            logging.debug(f"Getting metadata: {filename}")
            return _to_dt(stat.st_ctime), _to_dt(stat.st_mtime), stat.st_size
        else:
            raise ValueError(f"Not Found: {filename}")

    def get_permissions(self, filename):
        """
        Get permissions of filename

        :param filename: name of file
        :return: permissions (oct), if file is valid, else False
        """
        if os.path.isfile(filename) and (not os.path.isdir(filename)):
            logging.debug(f"Getting permissions: {filename}")
            return oct(os.stat(filename).st_mode)
        else:
            raise ValueError(f"Not Found: {filename}")

    def set_permissions(self, filename, permissions):
        """
        Set permissions to file

        :param filename: name of file
        :param permissions: permissions of file in UNIX format, e.g 0777
        :return: True, if file is valid, else False
        """
        if os.path.isfile(filename) and (not os.path.isdir(filename)):
            logging.debug(f"Setting {permissions} to: {filename}")
            os.chmod(filename, permissions)
            return True
        else:
            raise ValueError(f"Not Found: {filename}")
