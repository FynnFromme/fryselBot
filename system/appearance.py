from fryselBot.database import select, update
from fryselBot.utilities import util

from discord.ext.commands import Context
from discord import Embed

from itertools import cycle


# Names
bot_name = "fryselBot"
version = "1.0"


# Default values
default_prefix = "+"

default_primary_color: hex = 0xf5c140
default_secondary_color: hex = 0x168aa3
red_color: hex = 0xc94435
green_color: hex = 0x3d9757


# Status of the bot                                                   # Newest function of the bot
status = cycle(["Hey there!", f"v. {version} | {default_prefix}help", "New Custom Prefixes!"])


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


def set_prefix(guild_id: int, prefix) -> None:
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


async def prefix_command(ctx: Context, prefix: str) -> None:
    """
    Command for setting prefix on guild.
    :param ctx: Context of the command call
    :param prefix: The given prefix
    :raises InvalidInputError: When the given prefix isn't 'default' or a single character
    """
    # Delete message of member
    await ctx.message.delete()

    if prefix.lower() == "default":
        # Set prefix to default value
        set_prefix(guild_id=ctx.guild.id, prefix=None)
        prefix = default_prefix
    else:
        # Set prefix of the guild to given prefix
        set_prefix(guild_id=ctx.guild.id, prefix=prefix)

    # Send response to command
    await ctx.send(embed=Embed(description=f"The **prefix** was set to `{prefix}`",
                               colour=get_secondary_color(ctx.guild.id)))


# Primary Color functions
def get_primary_color(guild_id: int) -> hex:
    """
    Provides the primary_color for a specific guild
    :param guild_id: Discord GuildID
    :return: Primary color for the guild
    """
    # Get primary color out of database
    db_color = select.primary_color(guild_id=guild_id)

    # Either return the primary color of the guild or the default primary color
    return db_color if db_color else default_primary_color


def set_primary_color(guild_id: int, primary_color) -> None:
    """
    Sets the prefix for a specific guild
    :param guild_id: Discord GuildID
    :param primary_color: PrimaryColor for the guild
    :raises: InvalidInputError when the prefix is invalid
    """
    if primary_color and type(primary_color) != int:
        raise util.InvalidInputError(primary_color, "primary_color has to be an integer")

    update.primary_color(value=primary_color, argument=guild_id)


async def primary_color_command(ctx: Context, primary_color: str) -> None:
    """
    Command for setting primary color on guild.
    :param ctx: Context of the command call
    :param primary_color: The given primary color hex-code
    :raises InvalidInputError: When the given primary_color isn't 'default', hex-color code or integer
    """
    # Delete message of member
    await ctx.message.delete()

    if primary_color == "default":
        # Set primary color to default value
        set_primary_color(guild_id=ctx.guild.id, primary_color=None)
        primary_color = default_primary_color
    else:
        try:
            # Set primary_color to valid integer
            if primary_color.startswith("#"):
                primary_color = int("0x" + primary_color[1:], 16)

            elif primary_color.startswith("0x"):
                primary_color = int(primary_color, 16)

            else:
                primary_color = int("0x" + primary_color, 16)

            # Set primary color of the server
            set_primary_color(guild_id=ctx.guild.id, primary_color=primary_color)
        except TypeError:
            raise util.InvalidInputError(primary_color, "primary_color has to be an hex-code or integer")

    # Send response to command
    await ctx.send(embed=Embed(description="The **primary color** was updated",
                               colour=primary_color))


# Secondary color functions
def get_secondary_color(guild_id: int) -> hex:
    """
    Provides the secondary_color for a specific guild
    :param guild_id: Discord GuildID
    :return: Secondary color for the guild
    """
    # Get secondary color out of database
    db_color = select.secondary_color(guild_id=guild_id)

    # Either return the secondary color of the guild or the default secondary color
    return db_color if db_color else default_secondary_color


def set_secondary_color(guild_id: int, secondary_color) -> None:
    """
    Sets the prefix for a specific guild
    :param guild_id: Discord GuildID
    :param secondary_color: SecondaryColor for the guild
    :raises: InvalidInputError when the prefix is invalid
    """
    if secondary_color and type(secondary_color) != int:
        raise util.InvalidInputError(secondary_color, "secondary_color has to be an integer")

    update.secondary_color(value=secondary_color, argument=guild_id)


async def secondary_color_command(ctx: Context, secondary_color: str) -> None:
    """
    Command for setting secondary color on guild.
    :param ctx: Context of the command call
    :param secondary_color: The given secondary color hex-code
    :raises InvalidInputError: When the given secondary_color isn't 'default', hex-color code or integer
    """
    # Delete message of member
    await ctx.message.delete()

    if secondary_color == "default":
        # Set secondary color to default value
        set_secondary_color(guild_id=ctx.guild.id, secondary_color=None)
        secondary_color = default_secondary_color

    else:
        try:
            # Set secondary_color to valid integer
            if secondary_color.startswith("#"):
                secondary_color = int("0x" + secondary_color[1:], 16)

            elif secondary_color.startswith("0x"):
                secondary_color = int(secondary_color, 16)

            else:
                secondary_color = int("0x" + secondary_color, 16)

            # Set secondary color of the server
            set_secondary_color(guild_id=ctx.guild.id, secondary_color=secondary_color)
        except TypeError:
            raise util.InvalidInputError(secondary_color, "secondary_color has to be an hex-code or integer")

    # Send response to command
    await ctx.send(embed=Embed(description="The **secondary color** was updated",
                               colour=secondary_color))
