import random
from sqlite3 import Cursor
from typing import Optional

from discord import Guild, CategoryChannel, VoiceChannel, TextChannel, Role, Member, Message, PermissionOverwrite, \
    NotFound, Game, Activity
from discord.abc import GuildChannel

from fryselBot.database import insert, update, select, delete
from fryselBot.database.manager import connection, DatabaseEntryError
from fryselBot.database.select import PrivateRoom
from fryselBot.system import roles
from fryselBot.system.private_rooms import settings


def get_category(guild: Guild) -> CategoryChannel:
    """
    Get the private room category of a guild
    :param guild: Guild to get the categroy from
    :return: Private room category of guild
    """
    return guild.get_channel(select.pr_categroy_id(guild.id))


def get_cpr_channel(guild: Guild) -> VoiceChannel:
    """
    Get the create private room channel of a guild
    :param guild: Guild to get the channel from
    :return: Create private room channel of guild
    """
    return guild.get_channel(select.cpr_channel_id(guild.id))


def get_settings_channel(guild: Guild) -> TextChannel:
    """
    Get the private room settings channel of a guild
    :param guild: Guild to get the channel from
    :return: Private room settings channel of guild
    """
    return guild.get_channel(select.pr_settings_id(guild.id))


def is_cpr_channel(channel: VoiceChannel) -> bool:
    """
    Check whether the channel is the cpr (create private room) channel of a guild
    :param channel: Channel to check
    :return: Whether the channel is a cpr channel
    """
    return select.cpr_channel_id(channel.guild.id) == channel.id


def is_settings_channel(channel: TextChannel) -> bool:
    """
    Check whether the channel is a settings channel of a guild
    :param channel: Channel to check
    :return: Whether the channel is a settings channel
    """
    return select.pr_settings_id(channel.guild.id) == channel.id


def is_private_room(channel: VoiceChannel) -> bool:
    """
    Check whether the channel is a private room
    :param channel: Channel to check
    :return: Whether the channel is a private room
    """

    return (channel.id, channel.guild.id) in select.all_private_rooms()


def is_move_channel(channel: VoiceChannel) -> bool:
    """
    Check whether the channel is a move channel
    :param channel: Channel to check
    :return: Whether the channel is a move channel
    """

    return (channel.id, channel.guild.id) in select.all_move_channels()


def has_private_room(owner: Member) -> bool:
    """

    :param owner:
    :return:
    """
    try:
        select.PrivateRoom(owner.guild.id, owner_id=owner.id)
    except DatabaseEntryError:
        return False
    else:
        return True


async def setup_private_rooms(guild: Guild) -> None:
    """
    Setup private rooms for the guild
    :param guild:
    """
    # Create private room category
    category: CategoryChannel = await guild.create_category('PRIVATE ROOMS', reason='Setup private rooms')

    # Create cpr channel
    overwrites = {guild.default_role: PermissionOverwrite(speak=False)}
    cpr_channel: VoiceChannel = await guild.create_voice_channel('➕ Private Room', category=category,
                                                                 reason='Setup private rooms',
                                                                 overwrites=overwrites)

    # Add them to database
    update.pr_categroy_id(argument=guild.id, value=category.id)
    update.cpr_channel_id(argument=guild.id, value=cpr_channel.id)
    insert.default_pr_settings(guild_id=guild.id)

    # Setup settings channel
    await settings.setup_settings(guild)


async def disable(guild: Guild) -> None:
    """
    Disable private rooms on guild
    :param guild: Guild to disable private rooms
    """
    # Fetch channels
    pr_category: CategoryChannel = guild.get_channel(select.pr_categroy_id(guild.id))
    cpr_channel: VoiceChannel = guild.get_channel(select.cpr_channel_id(guild.id))
    settings_channel: TextChannel = guild.get_channel(select.pr_settings_id(guild.id))

    # Delete channels if they exist
    try:
        if settings_channel:
            await settings_channel.delete(reason='Disabled private rooms')
    except NotFound:
        pass

    try:
        if cpr_channel:
            await cpr_channel.delete(reason='Disabled private rooms')
    except NotFound:
        pass

    try:
        if pr_category:
            await pr_category.delete(reason='Disabled private rooms')
    except NotFound:
        pass

    # Remove from database
    update.pr_categroy_id(argument=guild.id, value=None)
    update.cpr_channel_id(argument=guild.id, value=None)
    update.pr_settings_id(argument=guild.id, value=None)
    delete.default_pr_settings(guild.id)


async def create_private_room(owner: Member) -> None:
    """
    Create a private room for the owner
    :param owner: Owner of private room
    """
    # Initialize variables
    guild: Guild = owner.guild
    category: CategoryChannel = get_category(guild)

    # Get moderation and admin roles
    mod_roles: list[Role] = roles.get_admin_roles(guild)
    mod_roles.extend(roles.get_moderator_roles(guild))

    # Add permissions for mod roles to the private room
    pr_overwrites = {}
    for role in mod_roles:
        pr_overwrites[role] = PermissionOverwrite(view_channel=True, connect=True)

    if select.default_pr_hidden(guild.id):
        pr_overwrites[guild.default_role] = PermissionOverwrite(view_channel=False)

    # Create private room
    pr_channel = await guild.create_voice_channel(settings.get_name(guild, owner), category=category,
                                                  overwrites=pr_overwrites,
                                                  user_limit=select.default_pr_user_limit(guild.id),
                                                  reason='Created private room')

    # Move owner into private room
    await owner.move_to(pr_channel, reason='Created private room')

    # Insert into database
    room_id = insert.private_room(room_channel_id=pr_channel.id, move_channel_id=None, owner_id=owner.id,
                                  guild_id=guild.id)

    # Insert room settings into database
    insert.pr_settings(room_id=room_id, hidden=select.default_pr_hidden(guild.id),
                       user_limit=select.default_pr_user_limit(guild.id))

    # Fetch database entry with settings
    private_room: PrivateRoom = select.PrivateRoom(guild_id=guild.id, room_channel_id=pr_channel.id)

    if select.default_pr_locked(guild.id):
        await settings.lock(guild, private_room)

    if select.default_pr_game_activity(guild.id):
        await settings.toggle_game_activity(guild, private_room)
        await settings.check_game_activity(guild, private_room)

    # Set the permissions for the owner
    await set_owner_permissions(owner, private_room)


async def leave_private_room(member: Member, channel: VoiceChannel) -> None:
    """
    Handles when a member leaves a private room
    :param member:
    :param channel:
    """
    guild: Guild = channel.guild

    # Fetch private room and the owner
    private_room: PrivateRoom = select.PrivateRoom(guild_id=guild.id, room_channel_id=channel.id)
    owner_id = private_room.owner_id

    # Check whether the owner left
    if member.id == owner_id:
        # Check whether there are members in the channel left
        if list(filter(lambda m: not m.bot, channel.members)):
            # Search for new owner and set permissions
            new_owner = random.choice(channel.members)
            await set_owner(new_owner, private_room)

        # Remove owner permissions of old owner
        owner = guild.get_member(owner_id)
        if owner:
            await remove_owner_permissions(owner, private_room)

        # Delete the channel if the channel is empty
        if not channel.members:
            await delete_private_room(guild, private_room)


async def set_owner_permissions(owner: Member, private_room: PrivateRoom) -> None:
    """
    Set owner permissions for owner
    :param owner: Owner to set permissions to
    :param private_room: Private room to set permission
    """
    guild: Guild = owner.guild

    # Get channels
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    if private_room.locked:
        move_channel: VoiceChannel = guild.get_channel(private_room.move_channel_id)
        await move_channel.set_permissions(owner, move_members=True, connect=False)

    # Set permissions in private room and move channel
    if pr_channel:
        await pr_channel.set_permissions(owner, move_members=True, connect=True)

    # Set permissions for owner in settings and cpr channel
    await get_settings_channel(guild).set_permissions(owner, view_channel=True)
    await get_cpr_channel(guild).set_permissions(owner, connect=False)


async def remove_owner_permissions(owner: Member, private_room: PrivateRoom) -> None:
    """
    Remove owner permissions
    :param owner: Owner to remove permissions from
    :param private_room: The private room of the owner
    """
    guild: Guild = owner.guild
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)

    if private_room.locked:
        move_channel: VoiceChannel = guild.get_channel(private_room.move_channel_id)
        try:
            if move_channel:
                await move_channel.set_permissions(owner, overwrite=None)
        except NotFound:
            pass

    # Reset permissions in private room and move channel if they exist
    try:
        if pr_channel:
            await pr_channel.set_permissions(owner, overwrite=None)
    except NotFound:
        pass

    # Reset permissions in cpr and settings channel if they exist
    settings_channel: TextChannel = get_settings_channel(guild)
    cpr_channel: VoiceChannel = get_cpr_channel(guild)

    try:
        if settings_channel:
            await get_settings_channel(guild).set_permissions(owner, overwrite=None)
    except NotFound:
        pass

    try:
        if cpr_channel:
            await get_cpr_channel(guild).set_permissions(owner, overwrite=None)
    except NotFound:
        pass


async def delete_private_room(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Delete a private room
    :param guild: Guild of private room
    :param private_room: PrivateRoom to delete
    """
    # Fetch channels
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)

    if private_room.locked:
        move_channel: VoiceChannel = guild.get_channel(private_room.move_channel_id)
        try:
            if move_channel:
                await move_channel.delete()
        except NotFound:
            pass

    # Delete channels if they exist
    try:
        if pr_channel:
            await pr_channel.delete()
    except NotFound:
        pass

    # Delete out of database
    delete.private_room(private_room.room_id)
    delete.pr_settings(private_room.room_id)


async def set_owner(owner: Member, private_room: PrivateRoom) -> None:
    """
    Set the owner of a private room
    :param owner: New owner
    :param private_room: PrivateRoom to set new owner
    """
    guild: Guild = owner.guild

    # Update database
    update.pr_owner_id(argument=private_room.room_id, value=owner.id)

    # Set owner permissions
    await set_owner_permissions(owner, private_room)

    # Edit the name of the private room
    name = settings.get_name(guild, owner)
    await settings.set_name(name, guild, private_room)


async def delete_old_channels(message: Message, guild: Guild):
    await message.delete()
    for channel in guild.channels:
        channel: GuildChannel = channel
        if channel.name in ['PRIVATE ROOMS']:
            await channel.delete()
        elif channel.name.endswith('Room'):
            await channel.delete()

    @connection
    def f(_c: Cursor):
        _c.execute('DELETE FROM private_rooms')
        _c.execute('DELETE FROM pr_settings')
        _c.execute('DELETE FROM default_pr_settings')
    f()


def get_gameactivity(member: Member) -> Optional[Activity]:
    """

    :param member:
    :return:
    """
    if isinstance(member.activity, Game):
        activity = member.activity
    else:
        for a in member.activities:
            if isinstance(a, Game):
                activity = a
                break
        else:
            activity = None

    return activity
