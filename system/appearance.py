from fryselBot.database import select, update
from fryselBot.utilities import util

from itertools import cycle


# Names
bot_name = "fryselBot"
version = "1.0"


# Default values
default_prefix = "+"

default_color: hex = 0xf5c140
red_color: hex = 0xc94435
green_color: hex = 0x3d9757


# Status of the bot                                                   # Newest function of the bot
status = cycle(["Hey there!", f"v. {version} | {default_prefix}help", "New Welcome System!"])


# Prefix functions
def get_prefix(guild_id: int) -> str:
    """
    Provides the prefix for a specific guild
    :param guild_id: Discord GuildID
    :return: Prefix for the guild
    """
    # Get prefix out of database
    db_prefix = select.prefix(guild_id=guild_id)

    # Either return the prefix of the guild or the default prefix
    return db_prefix if db_prefix else default_prefix


def set_prefix(guild_id: int, prefix=None) -> None:
    """
    Sets the prefix for a specific guild
    :param guild_id: Discord GuildID
    :param prefix: Prefix for the guild
    :raises: InvalidInputError when the prefix is invalid
    """
    # Check whether the prefix is correct
    if prefix:
        if type(prefix) != str or len(prefix) != 1:
            raise util.InvalidInputError(prefix, "Prefix must be a string of length 1")

    # Update prefix in database
    update.prefix(value=prefix, argument=guild_id)


# Primary Color functions
def get_color(guild_id: int) -> hex:
    """
    Provides the primary_color for a specific guild
    :param guild_id: Discord GuildID
    :return: Primary color for the guild
    """
    # Get primary color out of database
    db_color = select.color(guild_id=guild_id)

    # Either return the primary color of the guild or the default primary color
    return db_color if db_color else default_color


def set_color(guild_id: int, color=None) -> None:
    """
    Sets the prefix for a specific guild
    :param guild_id: Discord GuildID
    :param color: PrimaryColor for the guild
    :raises: InvalidInputError when the prefix is invalid
    """
    if color and type(color) != int:
        raise util.InvalidInputError(color, "primary_color has to be an integer")

    update.color(value=color, argument=guild_id)


