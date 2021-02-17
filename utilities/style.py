from fryselBot.database import select

# Names
bot_name = "fryselBot"
version = "1.0"

# Default values
default_prefix = "+"

# TODO: Setup commands for primary_color, secondary_color and prefix

_primary_color: hex = 0xf5c140
_secondary_color: hex = 0x168aa3
red_color: hex = 0xc94435
green_color: hex = 0x3d9757


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


def get_primary_color(guild_id: int) -> hex:
    """
    Provides the primary_color for a specific guild
    :param guild_id: Discord GuildID
    :return: Primary color for the guild
    """
    # Get primary color out of database
    db_color = select.primary_color(guild_id=guild_id)

    # Either return the primary color of the guild or the default primary color
    return db_color if db_color else _primary_color


def get_secondary_color(guild_id: int) -> hex:
    """
    Provides the secondary_color for a specific guild
    :param guild_id: Discord GuildID
    :return: Secondary color for the guild
    """
    # Get secondary color out of database
    db_color = select.secondary_color(guild_id=guild_id)

    # Either return the secondary color of the guild or the default secondary color
    return db_color if db_color else _secondary_color
