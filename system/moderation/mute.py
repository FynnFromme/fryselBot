from discord import Guild, Role, Permissions, TextChannel, Member, Message, Embed, Client
from datetime import datetime, timedelta

from fryselBot.database import delete, select, insert, update
from fryselBot.database.manager import DatabaseEntryError
from fryselBot.database.select import Mute
from fryselBot.utilities import secret, util
from fryselBot.system import appearance, permission
from fryselBot.system.moderation import moderation


async def create_mute_role(guild: Guild) -> Role:
    """
    Creates the mute role for the server
    :param guild: Server to create mute role for
    :return: Role that was created
    """
    # Setup permissions - Defaultpermissions with send_messages=False
    permissions: Permissions = guild.default_role.permissions
    permissions.update(send_messages=False)

    # Create mute role
    mute_role = await guild.create_role(name='Muted', permissions=permissions, reason='Mute role for fryselBot.')

    # Set position of role
    position = guild.get_member(secret.bot_id).top_role.position - 1
    await mute_role.edit(position=position)

    # Insert into database
    update.mute_role_id(argument=guild.id, value=mute_role.id)

    return mute_role


async def get_mute_role(guild: Guild) -> Role:
    """
    Get mute role of the guild. Either the existing one or a new one
    :param guild: Guild to get the mute role of
    :return: Mute role of the guild
    """
    # Fetch mute role id
    mute_role_id = select.mute_role_id(guild.id)
    mute_role = guild.get_role(mute_role_id)

    # Create new mute_role if the other one didn't exist anymore
    if not mute_role:
        mute_role = await create_mute_role(guild)
        # Setup mute role
        await setup_mute_in_guild(guild)

    return mute_role


async def setup_mute_in_guild(guild: Guild) -> None:
    """
    Sets the mute role permissions for all text channels of the guild
    :param guild: Guild to set permissions
    """
    mute_role = await get_mute_role(guild)

    # Add role permissions to all text_channels
    for channel in guild.text_channels:
        await channel.set_permissions(mute_role, send_messages=False)


async def setup_mute_in_channel(channel: TextChannel) -> None:
    """
    Sets the mute role permissions for the channel
    :param channel: TextChannel to set permissions
    """
    guild: Guild = channel.guild

    mute_role = await get_mute_role(guild)

    # Add role permissions to the channel
    await channel.set_permissions(mute_role, send_messages=False)


async def mute(member: Member, moderator: Member, reason: str = None) -> None:
    """
    Mute the member and send log message
    :param member: Member to mute
    :param moderator: Moderator of mute
    :param reason: Reason for mute
    """
    guild: Guild = member.guild

    # Send private message
    await moderation.private_message(member, f'You got muted on {guild.name}', moderator=moderator, Reason=reason)

    # Mute member
    mute_role = await get_mute_role(guild)
    await member.add_roles(mute_role, reason=reason)

    # Delete old mute entries in database
    delete.mutes_of_member(user_id=member.id, guild_id=guild.id)

    # Insert into database
    insert.mute(temp=True, user_id=member.id, mod_id=moderator.id, date=datetime.utcnow(), guild_id=guild.id,
                reason=reason)

    # Send log message in moderation log
    await moderation.log_message('Mute', member, moderator, guild, reason=reason, Duration='∞')


async def mute_cmd(message: Message, member: Member, reason: str = None) -> None:
    """
    Mute command that mutes a member on the guild
    :param message: Message of command call
    :param member: Member to be muted
    :param reason: Reason for mute
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't mute the bot
        raise Exception('Cannot mute the bot')

    if permission.is_mod(member=member):
        # Don't mute moderators of the server
        raise Exception('Cannot mute moderators')

    # Mute the member and send log message
    await mute(member, moderator, reason)

    # Send embed as response in chat
    await moderation.chat_message(channel, f'Muted {member.mention}', appearance.moderation_color, moderator)


async def unmute(member: Member, moderator: Member, reason: str = None) -> None:
    """
    Unmutes the member and sends log message
    :param member: Member to unmute
    :param moderator: Moderator who unmuted the member
    :param reason: Reason for unmute
    """
    guild: Guild = member.guild
    mute_role: Role = await get_mute_role(guild)

    # Send private message
    await moderation.private_message(member, f'You got unmuted on {guild.name}',  moderator=moderator,
                                     color=appearance.success_color, Reason=reason)

    # Remove mute role
    await member.remove_roles(mute_role, reason=f'Unmuted by {moderator.display_name}')

    # Delete mute entries in database
    delete.mutes_of_member(user_id=member.id, guild_id=guild.id)

    # Send log message in moderation log
    await moderation.log_message('Unmute', member, moderator, guild, color=appearance.success_color, reason=reason)


async def unmute_cmd(message: Message, member: Member) -> None:
    """
    Unmute user on the guild
    :param message: Message of command call
    :param member: Member to be unmuted
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    # Check whether the member is muted
    if not is_muted(member):
        raise Exception('Member is not muted')

    # Unmte member and send log message
    await unmute(member, moderator)

    # Send embed as response in chat
    await moderation.chat_message(channel, f'Unmuted {member.mention}', appearance.moderation_color, moderator)


async def tempmute(member: Member, moderator: Member, duration: str, tdelta: timedelta, reason: str = None) -> None:
    """
    Tempmutes the member and send log message
    :param member: Member to mute
    :param moderator: Moderator of mute
    :param duration: String represenation of timedelta
    :param tdelta: Timedelta of tempmute
    :param reason: Reason for mute
    """
    guild: Guild = member.guild

    # Get the date, the mute expires
    until_date = datetime.utcnow() + tdelta

    # Send private message
    await moderation.private_message(member, f'You got muted on {guild.name}', None, moderator, Duration=duration,
                                     Reason=reason)

    # Mute member
    mute_role = await get_mute_role(guild)
    await member.add_roles(mute_role, reason=reason)

    # Delete old mute entries in database
    delete.mutes_of_member(user_id=member.id, guild_id=guild.id)

    # Insert mute into database
    insert.mute(temp=True, user_id=member.id, mod_id=moderator.id, date=datetime.utcnow(), guild_id=guild.id,
                reason=reason, until_date=until_date)

    # Send log message in moderation log
    await moderation.log_message('Mute', member, moderator, guild, reason=reason, Duration=duration)


async def tempmute_cmd(message: Message, member: Member, duration_amount: int, duration_unit: str,
                       reason: str = None) -> None:
    """
    Tempmute member on the guild
    :param message: Message of command call
    :param member: Member to be muted
    :param duration_amount: Duration of mute (e.g. 60)
    :param duration_unit: Unit of duration (e.g. 'minutes', 'hours')
    :param reason: Reason for mute
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't mute the bot
        raise Exception('Cannot mute the bot')

    # Don't mute moderators of the server
    if permission.is_mod(member=member):
        raise Exception('Cannot mute moderators')

    tdelta, duration = moderation.get_duration(duration_amount, duration_unit)

    # Mute member and send log message
    await tempmute(member, moderator, duration, tdelta, reason)

    # Send embed as response in chat
    await moderation.chat_message(channel, f'Muted {member.mention} for {duration}', appearance.moderation_color,
                                  moderator)


async def check_expired(client: Client) -> None:
    """
    Handles expired temporary mutes
    :param client: Bot client
    """
    # Fetch expired mutes
    expired_mutes: list[Mute] = select.expired_mutes()

    # Unmute them
    for mute_entry in expired_mutes:
        # Initialize variables
        guild: Guild = client.get_guild(mute_entry.guild_id)
        member: Member = guild.get_member(mute_entry.user_id)
        bot_user = client.user

        # Remove mute role from member
        if member:
            await unmute(member, bot_user, reason='Temporary mute expired')

        # Delete out of database
        delete.mute(argument=mute_entry.mute_id)


def is_muted(member: Member) -> bool:
    """
    Checks whether the member is muted
    :param member: Member to check
    :return: Whether the member is muted
    """
    # Select mute if exists
    try:
        # Throws an error in cas no mute exists
        select.Mute(member.guild.id, member.id)
    except DatabaseEntryError:
        return False
    else:
        return True
