import os
import random
import string


def generate_random(n: int) -> str:
    """
    Generate random string
    :param n: length of string
    :return: generated string
    """
    name = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(n)])
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
