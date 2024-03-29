from database import insert, delete, select
from system import welcome, moderation

from discord import Guild, Client, Role, VoiceChannel, Member

from system import private_rooms as pr_sys
from system.moderation import mute, moderation
from system.private_rooms import private_rooms


async def join_guild(guild: Guild) -> None:
    """
    Handles joining a new guild.
    :param guild: Guild that is joined
    """
    insert.guild(guild_id=guild.id)
    insert.guild_settings(guild_id=guild.id)

    # Setup mute
    await mute.setup_mute_in_guild(guild)


def remove_guild(guild: Guild) -> None:
    """
    Handles removing a guild.
    :param guild: Guild that is removed
    """
    delete.all_entries_of_guild(guild_id=guild.id)


async def check_guilds(client: Client) -> None:
    """
    Checks for guilds left / joined.
    :param client: Bot client
    """
    # Get list of all active guild_ids and guild_ids in database
    active_guilds = client.guilds
    active_guild_ids = list(map(lambda g: g.id, active_guilds))
    db_guild_ids = select.all_guilds()

    # Check for new guilds and add them to database
    for guild in active_guilds:
        if guild.id not in db_guild_ids:
            join_guild(client.get_guild(guild.id))

        # Setup mute
        await mute.setup_mute_in_guild(guild)

    # Check for guilds left and remove them from database
    for guild_id in db_guild_ids:
        if guild_id not in active_guild_ids:
            delete.all_entries_of_guild(guild_id=guild_id)

    # Server count
    print(f'The bot is currently on {len(active_guild_ids)} servers.')


async def check_channels(client: Client) -> None:
    """
    Checks for deleted channels.
    :param client: Bot client
    """
    # Welcome System:List of pairs of channel_ids and guild_ids
    # Iterate through channels
    for channel_id, guild_id in select.all_welcome_channels():
        guild: Guild = client.get_guild(guild_id)
        # Check if the channel exists
        if channel_id not in list(map(lambda c: c.id, guild.channels)):
            # Welcome System: Remove channel out of database and set welcome/leave messages to disabled
            welcome.toggle_welcome(guild, disable=True)
            welcome.toggle_leave(guild, disable=True)
            welcome.set_welcome_channel(guild, channel_id=None)

    # Moderation Log: List of pairs of channel_ids and guild_ids
    # Iterate through channels
    for channel_id, guild_id in select.all_moderation_logs():
        guild: Guild = client.get_guild(guild_id)
        # Check if the channel exists
        if channel_id not in list(map(lambda c: c.id, guild.channels)):
            # Moderation System: Delete the moderation log
            moderation.set_mod_log(guild, channel_id=None)

    # Private_rooms: List of pairs of channel_ids and guild_ids
    # Iterate through channels
    for channel_id, guild_id in select.all_private_rooms():
        guild: Guild = client.get_guild(guild_id)
        private_room = select.PrivateRoom(guild_id=guild.id, room_channel_id=channel_id)
        owner = guild.get_member(private_room.owner_id)
        # Check if the channel exists
        if channel_id not in list(map(lambda c: c.id, guild.channels)):
            # Reset permissions for owner
            await private_rooms.remove_owner_permissions(owner, private_room)
            # Private rooms: Delete private room
            await private_rooms.delete_private_room(guild, private_room)
        else:
            # Check the members of the private room
            channel: VoiceChannel = guild.get_channel(channel_id)
            members: list[Member] = channel.members
            # Delete if the room is empty
            if not members:
                await private_rooms.remove_owner_permissions(owner, private_room)
                await private_rooms.delete_private_room(guild, private_room)
            else:
                if owner in members:
                    # Do nothing if the owner is in the channel
                    pass
                else:
                    # Reset permissions for owner and find new owner
                    await private_rooms.leave_private_room(owner, channel)

    # Move channels: List of pairs of channel_ids and guild_ids
    # Iterate through channels
    for channel_id, guild_id in select.all_move_channels():
        guild: Guild = client.get_guild(guild_id)
        # Check if the channel exists
        if channel_id not in list(map(lambda c: c.id, guild.channels)):
            # Private rooms: Unlock private room
            private_room = select.PrivateRoom(guild_id=guild.id, move_channel_id=channel_id)
            await pr_sys.settings.unlock(guild, private_room)

    # PR Text channels: List of pairs of channel_ids and guild_ids
    # Iterate through channels
    for channel_id, guild_id in select.all_pr_text_channels():
        guild: Guild = client.get_guild(guild_id)
        # Check if the channel exists
        if channel_id not in list(map(lambda c: c.id, guild.channels)):
            # Private rooms: Unlock private room
            private_room = select.PrivateRoom(guild_id=guild.id, text_channel_id=channel_id)
            await private_rooms.delete_private_room(guild, private_room)

    # Cpr channels: List of pairs of channel_ids and guild_ids
    channels = select.all_cpr_channels()
    channels.extend(select.all_pr_settings())
    channels.extend(select.all_pr_categories())

    # Iterate through channels
    for channel_id, guild_id in channels:
        guild: Guild = client.get_guild(guild_id)
        # Check if the channel exists
        if channel_id not in list(map(lambda c: c.id, guild.channels)):
            # Private rooms: Delete private room
            await private_rooms.disable(guild)


def check_roles(client: Client) -> None:
    """
    Checks for deleted roles.
    :param client: Bot client
    """
    # List of pairs of role_ids and guild_ids
    roles = select.all_roles()

    # Iterate through channels
    for role_id, guild_id in roles:
        guild: Guild = client.get_guild(guild_id)
        # Check if the role exists
        if role_id not in list(map(lambda c: c.id, guild.roles)):
            # Remove role out of database
            delete.role(role_id)


async def check_members(client: Client) -> None:
    """
    Checks for members joined
    :param client: Bot client
    """
    guilds: list[Guild] = client.guilds

    for guild in guilds:
        for member in guild.members:
            if mute.is_muted(member):
                mute_role: Role = await mute.get_mute_role(guild)
                if mute_role not in member.roles:
                    await member.add_roles(mute_role, reason='Member is muted')


# Checks that can be done after rebooting to set database up to date
checks = {check_roles}
async_checks = {check_guilds, check_members, check_channels}
