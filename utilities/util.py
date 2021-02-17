from datetime import datetime
import random


def iso_to_datetime(s: str) -> datetime:
    """
    Create datetime object form date as iso format
    :param s: Date in '%Y-%m-%d %H:%M:%S'
    :return: Datetime object
    """
    if s is None:
        raise Exception("Invalid Input (iso_to_datetime)")

    year_ = int(s[0:4])
    month_ = int(s[5:7])
    day_ = int(s[8:10])
    hour_ = int(s[11:13])
    minute_ = int(s[14:16])
    second_ = int(s[17:19])
    return datetime(year=year_, month=month_, day=day_, hour=hour_, minute=minute_, second=second_)


def random_base_16_code() -> str:
    """
    Generate random base 16 code that is 5 digits long
    :return:
    """
    code = "".join(random.choice("0123456789abcdef") for _ in range(5))
    return code
