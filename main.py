#! /usr/bin/env python3
import argparse
import os
import yaml
import logging
import logging.config
from src.file_service import RawFileService, SignedFileService, EncryptedFileService
from src.config import Config

file_service = RawFileService()
signed_file_service = SignedFileService(file_service)
encrypted_file_service = EncryptedFileService(file_service)


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
        data = signed_file_service.read(filename)
        print(f"Reading file: {filename}")
        print(data)
    except Exception as e:
        print(e)


def read_encrypted():
    filename = input('Enter file name: ')
    try:
        data = encrypted_file_service.read(filename)
        print(f"Reading file: {filename}")
        print(data)
    except Exception as e:
        print(e)


def delete_file():
    filename = input('Enter file name: ')
    try:
        file_service.remove(filename)
        print(f"Delete file: {filename}")
    except Exception as e:
        print(e)


def list_dir():
    print("list_dir")
    print(file_service.ls())


def change_dir():
    directory = input("Enter dir name: ")
    try:
        file_service.cd(directory)
        print(f"Change dir: {directory}")
    except Exception as e:
        print(e)


def create_file():
    content = input("Enter file content: ")
    filename = file_service.create(content)
    print(f"Creating file {filename} with content: \n{content}")


def create_signed_file():
    content = input("Enter file content: ")
    filename = signed_file_service.create(content)
    print(f"Creating signed file {filename} with content: \n{content}")


def create_encrypted_file():
    content = input("Enter file content: ")
    filename = encrypted_file_service.create(content)
    print(f"Creating encrypted file {filename} with content: \n{content}")


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
        result = file_service.read_metadata(filename)
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
        "create_signed": create_signed_file,
        "read_encrypted": read_encrypted,
        "create_encrypted": create_encrypted_file
    }
    parser = argparse.ArgumentParser(description="Restful server")
    parser.add_argument('-d', '--directory', dest='path', help='Set working directory', default='.')
    args = parser.parse_args()
    directory = args.path
    file_service.cd(directory)
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
