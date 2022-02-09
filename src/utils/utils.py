import os
import random
import string
import logging


def generate_random(length: int) -> str:
    """
    Generate random string

    :param length: length of string
    :return: generated string
    """
    name = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])
    logging.debug(f"Generating string: {name}")
    return name


def generate_name(length: int) -> str:
    """
    Generate unique filename

    :param length: length of name
    :return: generated name
    """
    name = generate_random(length)
    while os.path.isfile(name) or os.path.isdir(name):
        name = generate_random(length)
    return name
