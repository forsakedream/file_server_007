import os
import logging
from typing import Union
from datetime import datetime as dt
from src import utils


def read(filename: str) -> Union[str, bool]:
    """
    Read file from disk by filename

    :param filename: name of file
    :return: file content, if file exists, else False
    """
    if os.path.isfile(filename) and (not os.path.isdir(filename)):
        logging.debug(f"Opening: {filename}")
        with open(filename, 'r') as file:
            return file.read()
    else:
        logging.debug(f"Not Found: {filename}")
        return False


def delete(filename: str) -> bool:
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
        logging.debug(f"Not Found: {filename}")
        return False


def list_dir() -> list:
    """
    Return list of files and directories in the current directory

    :return: list of files and directories in the current directory
    """
    logging.debug(f"Listing directories in current dir")
    return os.listdir()


def get_file_meta_data(filename: str) -> Union[tuple, bool]:
    """
    Read file creation date, edit date, filesize

    :param filename:
    :return tuple (create_date, modification_date, filesize), file exists, else False
    """
    if os.path.isfile(filename) and (not os.path.isdir(filename)):
        stat = os.stat(filename)
        logging.debug(f"Getting metadata: {filename}")
        return _to_dt(stat.st_ctime), _to_dt(stat.st_mtime), stat.st_size
    else:
        logging.debug(f"Not Found: {filename}")
        return False


def change_dir(directory: str) -> bool:
    """
    Change current directory

    :param directory: name of directory
    :return: True, if desired directory is valid, else False
    """
    if os.path.isdir(directory):
        logging.debug(f"Changing dir to: {directory}")
        os.chdir(directory)
        return True
    else:
        logging.debug(f"Not Found: {directory}")
        return False


def create(content: str) -> str:
    """
    Create file with unique file name and desired content

    :param content: content of created file
    :return: unique filename
    """
    filename = utils.generate_name(10)
    logging.debug(f"Generated name: {filename}")
    create_file(filename, content)
    return filename


def create_file(filename: str, content: str) -> None:
    """
    Write content to file

    :param filename: name of file
    :param content: content of file
    """
    logging.debug(f"Writing to: {filename}\nContent: {content}")
    with open(filename, "w") as file:
        file.write(content)


def get_permissions(filename: str) -> Union[str, bool]:
    """
    Get permissions of filename

    :param filename: name of file
    :return: permissions (oct), if file is valid, else False
    """
    if os.path.isfile(filename) and (not os.path.isdir(filename)):
        logging.debug(f"Getting permissions: {filename}")
        return oct(os.stat(filename).st_mode)
    else:
        logging.debug(f"Not Found: {filename}")
        return False


def set_permissions(filename: str, permissions: int) -> bool:
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
        logging.debug(f"Not Found: {filename}")
        return False


def _to_dt(time: float) -> str:
    return dt.utcfromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")
