"""
File utilities
"""

import errno
import json
from os import strerror
from pathlib import Path


def check_file_exists(fpath: Path) -> None:
    """
    Checks if the file exists and is a file
    :raise FileNotFoundError: If the file does not exist
    :param fpath: The path to the file
    :return: None
    """
    if not fpath.exists() or not fpath.is_file():
        raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), fpath.as_posix())


def check_file_not_exists(fpath: Path) -> None:
    """
    Checks if the file does not exist
    :raise FileExistsError: If the file exists
    :param fpath: The path to the file
    :return: None
    """
    if fpath.exists():
        raise FileExistsError(errno.EEXIST, strerror(errno.EEXIST), fpath.as_posix())


def load_file(fpath: Path) -> str:
    """
    Reads the text file and return its contents

    :param fpath: The path of the file
    :return: text: The contents of the file
    """
    check_file_exists(fpath)
    with open(fpath, encoding="utf-8") as file:
        text = file.read()
    return text.strip()


def load_json_file(fpath: Path) -> dict:
    """
    Reads the json file and return its contents as a dictionary

    :param fpath: The path of the file
    :return: text: The contents of the file
    """
    check_file_exists(fpath)
    with open(fpath, encoding="utf-8") as file:
        output_json = json.load(file)
    return output_json


def dump_file(fpath: Path, data: str) -> None:
    """
    Write data to a text file

    :param fpath: The path of the file
    :param data: The data to write to the file
    :return: None
    """
    with open(fpath, "w", encoding="utf-8") as file:
        file.write(data)


def dump_json_file(fpath: Path, data: dict) -> None:
    """
    Write json dict to a file

    :param fpath: The path of the file
    :param data: The data to write to the file
    :return: None
    """
    dump_file(fpath, json.dumps(data, indent=4))
