import os


def read(filename):
    with open(filename, 'r') as file:
        data = file.read()
        return data


def delete(filename):
    os.remove(filename)


def list_dir():
    return os.listdir()


def change_dir(directory):
    os.chdir(directory)


def create(filename, content):
    with open(filename, "w") as file:
        file.write(content)


def get_permissions(filename):
    return oct(os.stat(filename).st_mode)


def set_permissions(filename, permissions):
    os.chmod(filename, permissions)
