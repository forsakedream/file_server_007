#! /usr/bin/env python3
import argparse
import os
from src import file_service
from src import utils


def read_file():
    filename = input('Enter file name: ')
    if os.path.isfile(filename):
        print(f"Reading file: {filename}")
        print(file_service.read(filename))
    else:
        print("File doesn't exists in current directory!")


def delete_file():
    filename = input('Enter file name: ')
    if os.path.isfile(filename):
        print(f"Delete file: {filename}")
        file_service.delete(filename)
    else:
        print("File doesn't exists in current directory!")


def list_dir():
    print("list_dir")
    print(file_service.list_dir())


def change_dir():
    directory = input("Enter dir name: ")
    if os.path.isdir(directory):
        print(f"Change dir: {directory}")
        file_service.change_dir(directory)
    else:
        print("Directory doesn't exists!")


def create_file():
    content = input("Enter file content: ")
    filename = utils.generate_name(10)
    print(f"Creating file {filename} with content: \n{content}")
    file_service.create(filename, content)


def get_file_permissions():
    filename = input('Enter file name: ')
    if os.path.isfile(filename):
        permissions = file_service.get_permissions(filename)
        print(f'Permissions: {permissions}')
    else:
        print("File doesn't exists in current directory!")


def set_file_permissions():
    filename = input('Enter file name: ')
    if os.path.isfile(filename):
        permissions = int(input("Enter UNIX permissions in oct format: "))
        print(f'Set {permissions} to filename {filename}')
        file_service.set_permissions(filename, permissions)
    else:
        print("File doesn't exists in current directory!")


def main():
    commands = {
        "get": read_file,
        "create": create_file,
        "delete": delete_file,
        "ls": list_dir,
        "cd": change_dir,
        "get_permissions": get_file_permissions,
        "set_permissions": set_file_permissions
    }
    parser = argparse.ArgumentParser(description="Restful server")
    parser.add_argument('-d', '--directory', dest='path', help='Set working directory', default='.')
    args = parser.parse_args()
    directory = args.path
    os.chdir(directory)
    while True:
        command = input("Enter command: ")
        if command == "exit":
            return
        if command not in commands:
            print('Unknown command')
            continue
        command = commands[command]
        try:
            command()
        except Exception as ex:
            print(f"Error on {command} execution: {ex}")


if __name__ == "__main__":
    main()
