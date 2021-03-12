from datetime import datetime
import random
from typing import Optional

from discord import Message, NotFound


async def delete_message(message: Message) -> None:
    """
    Deletes the given message if it exists
    :param message: Message to be deleted
    """
    # Delete message of member if it isn't already
    if message:
        try:
            await message.delete()
        except NotFound:  # Message already deleted
            pass


class InvalidInputError(Exception):
    """
    Attributes:
        input: The input that was invalid
    Arguments:
        _input: The input that was invalid
    """
    def __init__(self, _input, *args):
        self.input = _input
        super().__init__(*args)


def iso_to_datetime(s: str) -> Optional[datetime]:
    """
    Create datetime object form date as iso format
    :param s: Date in '%Y-%m-%d %H:%M:%S'
    :return: Datetime object
    """
    if s is None:
        return None

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
    code = ''.join(random.choice('0123456789abcdef') for _ in range(5))
    return code
