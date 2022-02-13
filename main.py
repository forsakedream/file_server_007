#! /usr/bin/env python3
import argparse
import os
import yaml
import logging
import logging.config
from src import file_service
from src.config import Config


def read_file():
    filename = input('Enter file name: ')
    try:
        data = file_service.read(filename)
        print(f"Reading file: {filename}")
        print(data)
    except Exception as e:
        print(e)


def read_signed_file():
    filename = input('Enter file name: ')
    try:
        data = file_service.read_signed(filename)
        print(f"Reading file: {filename}")
        print(data)
    except Exception as e:
        print(e)


def delete_file():
    filename = input('Enter file name: ')
    try:
        file_service.delete(filename)
        print(f"Delete file: {filename}")
    except Exception as e:
        print(e)


def list_dir():
    print("list_dir")
    print(file_service.list_dir())


def change_dir():
    directory = input("Enter dir name: ")
    try:
        file_service.change_dir(directory)
        print(f"Change dir: {directory}")
    except Exception as e:
        print(e)


def create_file():
    content = input("Enter file content: ")
    filename = file_service.create(content)
    print(f"Creating file {filename} with content: \n{content}")


def create_signed_file():
    content = input("Enter file content: ")
    config = Config()
    signer = config.get_algo()
    filenames = file_service.create_signed(content, signer)
    print(f"Creating file {filenames[0]} and signature file {filenames[1]}, with content: \n{content}")


def get_file_permissions():
    filename = input('Enter file name: ')
    try:
        permissions = file_service.get_permissions(filename)
        print(f'Permissions: {permissions}')
    except Exception as e:
        print(e)


def set_file_permissions():
    filename = input('Enter file name: ')
    try:
        permissions = int(input("Enter UNIX permissions in oct format: "))
        file_service.set_permissions(filename, permissions)
        print(f'Setting {permissions} to filename {filename}')
    except Exception as e:
        print(e)


def get_file_metadata():
    filename = input('Enter file name: ')
    try:
        result = file_service.get_file_meta_data(filename)
        creation_date, modification_date, filesize = result
        print(f'Creation date: {creation_date}\n'
              f'Modification date: {modification_date}\n'
              f'File size: {filesize} Bytes')
    except Exception as e:
        print(e)


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
    config = Config()
    config.load("config.ini")
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
