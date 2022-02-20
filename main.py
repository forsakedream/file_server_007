#! /usr/bin/env python3
import argparse
import os
import yaml
import logging
import logging.config
from aiohttp import web
from src.config import Config
from src.cli_app import ConsoleApp
from src.http_server import create_web_app


def console_main(directory):
    cli = ConsoleApp(directory)
    commands = {
        "read": cli.read,
        "create": cli.create,
        "delete": cli.delete,
        "ls": cli.ls,
        "cd": cli.cd,
        "get_permissions": cli.get_permissions,
        "set_permissions": cli.set_permissions,
        "get_metadata": cli.get_metadata
    }

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


def http_main(directory):
    app = create_web_app(directory)
    web.run_app(app)


def main():
    parser = argparse.ArgumentParser(description="Restful server")
    parser.add_argument('-d', '--directory', dest='path', help='Set working directory', default='./files')
    parser.add_argument('-m', '--mode', dest='mode', help='Set working mode (web, console)', default='console')
    args = parser.parse_args()
    directory = args.path
    mode = args.mode
    if not os.path.exists("log"):
        os.mkdir("log")
    with open(file="./logging_config.yaml", mode='r') as file:
        logging_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
        logging.config.dictConfig(config=logging_yaml)
    logging.debug(f"Starting {mode} application in '{directory}'")
    config = Config()
    config.load("config.ini")
    if mode == "console":
        console_main(directory)
    elif mode == "web":
        http_main(directory)


if __name__ == "__main__":
    main()
