#! /usr/bin/env python3
import argparse
import os
import shutil
import yaml
import logging
import logging.config
from src import file_service


def read_file():
    filename = input('Enter file name: ')
    data = file_service.read(filename)
    if data:
        print(f"Reading file: {filename}")
        print(data)
    else:
        print("File doesn't exists in current directory!")


def read_signed_file():
    filename = input('Enter file name: ')
    data = file_service.read_signed(filename)
    if data:
        print(f"Reading file: {filename}")
        print(data)
    else:
        print("File doesn't exists in current directory!")


def delete_file():
    filename = input('Enter file name: ')
    result = file_service.delete(filename)
    if result:
        print(f"Delete file: {filename}")
    else:
        print("File doesn't exists in current directory!")


def list_dir():
    print("list_dir")
    print(file_service.list_dir())


def change_dir():
    directory = input("Enter dir name: ")
    result = file_service.change_dir(directory)
    if result:
        print(f"Change dir: {directory}")
    else:
        print("Directory doesn't exists!")


def create_file():
    content = input("Enter file content: ")
    filename = file_service.create(content)
    print(f"Creating file {filename} with content: \n{content}")


def create_signed_file():
    content = input("Enter file content: ")
    signer = input("Enter signer (md5, sha512): ")
    filenames = file_service.create_signed(content, signer)
    print(f"Creating file {filenames[0]} and signature file {filenames[1]}, with content: \n{content}")


def get_file_permissions():
    filename = input('Enter file name: ')
    permissions = file_service.get_permissions(filename)
    if permissions:
        print(f'Permissions: {permissions}')
    else:
        print("File doesn't exists in current directory!")


def set_file_permissions():
    filename = input('Enter file name: ')
    permissions = int(input("Enter UNIX permissions in oct format: "))
    result = file_service.set_permissions(filename, permissions)
    if result:
        print(f'Setting {permissions} to filename {filename}')
    else:
        print("File doesn't exists in current directory!")


def get_file_metadata():
    filename = input('Enter file name: ')
    result = file_service.get_file_meta_data(filename)
    if result:
        creation_date, modification_date, filesize = result
        print(f'Creation date: {creation_date}\n'
              f'Modification date: {modification_date}\n'
              f'File size: {filesize} Bytes')
    else:
        print("File doesn't exists in current directory!")


def main():
    commands = {
        "read": read_file,
        "create": create_file,
        "delete": delete_file,
        "ls": list_dir,
        "cd": change_dir,
        "get_permissions": get_file_permissions,
        "set_permissions": set_file_permissions,
        "get_metadata": get_file_metadata,
        "read_signed": read_signed_file,
        "create_signed": create_signed_file
    }
    parser = argparse.ArgumentParser(description="Restful server")
    parser.add_argument('-d', '--directory', dest='path', help='Set working directory', default='.')
    args = parser.parse_args()
    directory = args.path
    file_service.change_dir(directory)
    if not os.path.exists("log"):
        os.mkdir("log")
    with open(file="./logging_config.yaml", mode='r') as file:
        logging_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
        logging.config.dictConfig(config=logging_yaml)
    logging.debug(f"Starting application in {directory}")
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
