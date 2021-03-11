from fryselBot.database import insert, select, delete
from fryselBot.system import welcome, moderation

from discord import Guild, Client


def join_guild(guild: Guild) -> None:
    """
    Handles joining a new guild.
    :param guild: Guild that is joined
    """
    insert.guild(guild_id=guild.id)
    insert.guild_settings(guild_id=guild.id)
    # TODO: Welcome message (Introduce and help command)


def remove_guild(guild: Guild) -> None:
    """
    Handles removing a guild.
    :param guild: Guild that is removed
    """
    delete.all_entries_of_guild(guild_id=guild.id)


def check_guilds(client: Client) -> None:
    """
    Checks for guilds left / joined.
    :param client: Bot client
    """
    # Get list of all active guild_ids and guild_ids in database
    active_guild_ids = list(map(lambda g: g.id, client.guilds))
    db_guild_ids = select.all_guilds()

    # Check for new guilds and add them to database
    for guild_id in active_guild_ids:
        if guild_id not in db_guild_ids:
            join_guild(client.get_guild(guild_id))

    # Check for guilds left and remove them from database
    for guild_id in db_guild_ids:
        if guild_id not in active_guild_ids:
            delete.all_entries_of_guild(guild_id=guild_id)

    # Server count
    print(f'The bot is currently on {len(active_guild_ids)} servers.')


def check_channels(client: Client) -> None:
    """
    Checks for deleted channels.
    :param client: Bot client
    """
    # List of pairs of channel_ids and guild_ids
    channels = select.all_welcome_channels()

    # Iterate through channels
    for channel_id, guild_id in channels:
        guild: Guild = client.get_guild(guild_id)
        # Check if the channel exists
        if channel_id not in list(map(lambda c: c.id, guild.channels)):
            # Welcome System: Remove channel out of database and set welcome/leave messages to disabled
            welcome.toggle_welcome(guild, disable=True)
            welcome.toggle_leave(guild, disable=True)
            welcome.set_welcome_channel(guild, channel_id=None)

    # List of pairs of channel_ids and guild_ids
    channels = select.all_moderation_logs()
    # Iterate through channels
    for channel_id, guild_id in channels:
        guild: Guild = client.get_guild(guild_id)
        # Check if the channel exists
        if channel_id not in list(map(lambda c: c.id, guild.channels)):
            # Moderation System: Check whether the channel is the moderation log
            moderation.set_mod_log(guild, channel_id=None)


def check_roles(client: Client) -> None:
    """
    Checks for deleted roles.
    :param client: Bot client
    """
    # List of pairs of role_ids and guild_ids
    roles = select.all_moderation_roles()

    # Iterate through channels
    for role_id, guild_id in roles:
        guild: Guild = client.get_guild(guild_id)
        # Check if the role exists
        if role_id not in list(map(lambda c: c.id, guild.roles)):
            # Remove role out of database
            delete.role(role_id)


# Checks that can be done after rebooting to set database up to date
checks = {check_guilds, check_channels, check_roles}
