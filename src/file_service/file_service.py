import os
from src import utils


def read(filename):
    if os.path.isfile(filename) and (not os.path.isdir(filename)):
        with open(filename, 'r') as file:
            return file.read()
    else:
        return False


def delete(filename):
    if os.path.isfile(filename) and (not os.path.isdir(filename)):
        os.remove(filename)
        return True
    else:
        return False


def list_dir():
    return os.listdir()


def change_dir(directory):
    if os.path.isdir(directory):
        os.chdir(directory)
        return True
    else:
        return False


def create(content):
    filename = utils.generate_name(10)
    create_file(filename, content)
    return filename


def create_file(filename, content):
    with open(filename, "w") as file:
        file.write(content)


def get_permissions(filename):
    if os.path.isfile(filename) and (not os.path.isdir(filename)):
        return oct(os.stat(filename).st_mode)
    return False


def set_permissions(filename, permissions):
    if os.path.isfile(filename) and (not os.path.isdir(filename)):
        os.chmod(filename, permissions)
        return True
    return False
