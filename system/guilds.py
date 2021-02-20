from fryselBot.database import insert, select, delete

from discord import Guild, Client


def join_guild(guild: Guild) -> None:
    """
    Handles joining a new guild.
    :param guild: Guild that is joined
    :return: None
    """
    insert.guild(guild_id=guild.id)
    insert.guild_settings(guild_id=guild.id)
    # TODO: Welcome message (Introduce and help command)


def remove_guild(guild: Guild) -> None:
    """
    Handles removing a guild.
    :param guild: Guild that is removed
    :return: None
    """
    delete.all_entries_of_guild(guild_id=guild.id)


def check_guilds(client: Client) -> None:
    """
    Checks for guilds left / joined.
    :param client: Bot client
    :return: None
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
    print(f"The bot is currently on {len(active_guild_ids)} servers.")


