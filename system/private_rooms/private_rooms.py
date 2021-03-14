import asyncio
import random

from discord import Guild, CategoryChannel, VoiceChannel, TextChannel, Role, Member, Message, PermissionOverwrite, \
    NotFound
from discord.abc import GuildChannel

from fryselBot.database import insert, update, select, delete
from fryselBot.database.select import PrivateRoom
from fryselBot.system import roles


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


async def setup_private_rooms(guild: Guild) -> None:
    """
    Setup private rooms for the guild
    :param guild:
    """
    # Create private room category
    category: CategoryChannel = await guild.create_category('PRIVATE ROOMS', reason='Setup private rooms')

    # Create cpr channel
    cpr_channel: VoiceChannel = await guild.create_voice_channel('➕ Private Room', category=category,
                                                                 reason='Setup private rooms')

    # Create settings channel and set permissions
    settings_overwrites = {
        guild.default_role: PermissionOverwrite(view_channel=False, send_messages=False),
    }
    settings_channel: TextChannel = await guild.create_text_channel('settings', category=category,
                                                                    overwrites=settings_overwrites,
                                                                    reason='Setup private rooms')

    # Add them to database
    update.pr_categroy_id(argument=guild.id, value=category.id)
    update.cpr_channel_id(argument=guild.id, value=cpr_channel.id)
    update.pr_settings_id(argument=guild.id, value=settings_channel.id)

    # TODO: Send settings messages


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

    # Create private room
    private_room = await guild.create_voice_channel(f"{owner.display_name}'s Room", category=category,
                                                    overwrites=pr_overwrites,
                                                    reason='Created private room')

    # Create move channel and set permissions
    move_overwrites = {
        guild.default_role: PermissionOverwrite(view_channel=False),
    }
    move_channel = await guild.create_voice_channel(f'↑ Waiting for move ↑', category=category,
                                                    overwrites=move_overwrites,
                                                    reason='Created private room')

    # Move owner into private room
    await owner.move_to(private_room, reason='Created private room')

    # Set the permissions for the owner
    await set_owner_permissions(owner, private_room, move_channel)

    # Insert into database
    insert.private_room(room_channel_id=private_room.id, move_channel_id=move_channel.id, owner_id=owner.id,
                        guild_id=guild.id)


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
        if channel.members:
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


async def set_owner_permissions(owner: Member, pr_channel: VoiceChannel, move_channel: VoiceChannel) -> None:
    """
    Set owner permissions for owner
    :param owner: Owner to set permissions to
    :param pr_channel: The private room of the owner
    :param move_channel: The move channel of the owner
    """
    guild: Guild = owner.guild

    # Set permissions in private room and move channel
    await pr_channel.set_permissions(owner, move_members=True)
    await move_channel.set_permissions(owner, move_members=True, connect=False)

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
    move_channel: VoiceChannel = guild.get_channel(private_room.move_channel_id)

    # Reset permissions in private room and move channel
    if pr_channel:
        await pr_channel.set_permissions(owner, overwrite=None)
    if move_channel:
        await move_channel.set_permissions(owner, overwrite=None)

    # Reset permissions in cpr and settings channel
    await get_settings_channel(guild).set_permissions(owner, overwrite=None)
    await get_cpr_channel(guild).set_permissions(owner, overwrite=None)


async def delete_private_room(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Delete a private room
    :param guild: Guild of private room
    :param private_room: PrivateRoom to delete
    """
    # Fetch channels
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    move_channel: VoiceChannel = guild.get_channel(private_room.move_channel_id)

    # Delete channels if they exist
    try:
        if pr_channel:
            await pr_channel.delete()
    except NotFound:
        pass

    try:
        if move_channel:
            await move_channel.delete()
    except NotFound:
        pass

    # Delete out of database
    delete.private_room(private_room.room_id)


async def set_owner(owner: Member, private_room: PrivateRoom) -> None:
    """
    Set the owner of a private room
    :param owner: New owner
    :param private_room: PrivateRoom to set new owner
    """
    guild: Guild = owner.guild

    # Update database
    update.owner_id(argument=private_room.room_id, value=owner.id)

    # Fetch channels
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    move_channel: VoiceChannel = guild.get_channel(private_room.move_channel_id)

    # Set owner permissions
    await set_owner_permissions(owner, pr_channel, move_channel)

    # Edit the name of the private room
    await pr_channel.edit(name=f"{owner.display_name}'s Room")


async def delete_old_channels(message: Message, guild: Guild):
    await message.delete()
    for channel in guild.channels:
        channel: GuildChannel = channel
        if channel.name in ['PRIVATE ROOMS', '➕ Private Room', 'settings']:
            await channel.delete()
        elif channel.name.startswith('↑ Waiting') or channel.name.endswith('Room'):
            await channel.delete()
