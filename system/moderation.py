from datetime import datetime, timedelta
from typing import Union

import discord
from discord import TextChannel, Member, Embed, Guild, User, Client, Message, Forbidden, Permissions, Role

from fryselBot.database._manager import DatabaseEntryError
from fryselBot.database.select import Ban, Warn, Mute, Report
from fryselBot.system import appearance, description
from fryselBot.database import select, update, insert, delete
from fryselBot.utilities import secret, permission, util


def set_mod_log(guild: Guild, channel_id: int = None) -> None:
    """
    Set the moderation log for a guild
    :param guild: Guild to set the moderation log
    :param channel_id: Channel Id for moderation log
    """
    # Update mod log in database
    update.mod_log_id(argument=guild.id, value=channel_id)


def get_mod_log(guild: Guild) -> TextChannel:
    """
    Get the moderation log of a guild
    :param guild: Guild to get moderation log
    """
    # Get mod log ID out of database
    channel_id = select.mod_log_id(guild.id)

    # Get channel by ID
    channel = guild.get_channel(channel_id)
    return channel


async def log_message(operation: str, member: Union[User, Member], moderator: Member,
                      guild: Guild, reason: str = None, color: hex = 0xa82020, **kwargs) -> None:
    """
    Create a log message if the log message is set
    :param operation: Operation that is logged
    :param member: Member of operation
    :param moderator: Moderator of operation
    :param color: Color of embed
    :param reason: Reason for operation
    :param guild: Guild of operation
    :param kwargs: Additional fields for embed
    """
    # Send log message in moderation log
    mod_log: TextChannel = get_mod_log(guild)

    if mod_log:
        # Create embed and set up style
        log_embed: Embed = Embed(colour=color, timestamp=datetime.utcnow())

        log_embed.set_author(name=operation, icon_url=member.avatar_url)
        log_embed.set_footer(text=moderator.display_name, icon_url=moderator.avatar_url)

        log_embed.add_field(name='User', value=member.mention, inline=True)
        log_embed.add_field(name='Moderator', value=moderator.mention, inline=True)

        for k, v in kwargs.items():
            log_embed.add_field(name=k, value=v, inline=True)

        # Add reason in case it was given
        if reason:
            log_embed.add_field(name='Reason', value=reason, inline=False)

        await mod_log.send(embed=log_embed)


async def clear(message: Message, amount: int, ) -> None:
    """
    Deletes the latest amount messages in the channel
    :param message: Message of command call
    :param amount: Amount of messages that should be deleted
    """
    # Initialize varaibles
    channel: TextChannel = message.channel

    # Delete message of member
    await util.delete_message(message)

    # Delete one message at minimum
    if amount < 0:
        amount = 0
    # Only delete 100 messages at maximum
    if amount > 100:
        amount = 100

    # Delete the latest amount messages in the channel that are not pinned
    deleted = []
    async for msg in channel.history(limit=amount + 50):
        if not msg.pinned:
            deleted.append(msg)
            if len(deleted) == amount:
                break

    await channel.delete_messages(deleted)

    # Send confirmation and delete it after time
    embed = Embed(description=f'Deleted **{len(deleted)}** messages',
                  colour=appearance.moderation_color)

    msg = await channel.send(embed=embed)
    await msg.delete(delay=10)


async def clear_member(member: Member, message: Message, amount: int = 100) -> None:
    """
    Deletes the latest amount messages in the channel of member
    :param member: Member to delete messages of
    :param message: Message of command call
    :param amount: Amount of messages that should be deleted
    """
    # Initialize varaibles
    channel: TextChannel = message.channel

    # Delete message of member
    await util.delete_message(message)

    # Delete one message at minimum
    if amount < 0:
        amount = 0
    # Only delete 100 messages at maximum
    if amount > 100:
        amount = 100

    # Delete the latest amount messages in the channel that are from the member
    deleted = []
    async for msg in channel.history(limit=50000):
        if msg.author == member:
            deleted.append(msg)
            if len(deleted) == amount:
                break

    await channel.delete_messages(deleted)

    # Send confirmation and delete it after time
    embed = Embed(description=f'Deleted **{len(deleted)}** messages of {member.mention}',
                  colour=appearance.moderation_color)

    msg = await channel.send(embed=embed)
    await msg.delete(delay=10)


async def kick(message: Message, member: Member, reason: str = None) -> None:
    """
    Kick member on the guild
    :param message: Message of command call
    :param member: Member to be kicked
    :param reason: Reason for kick
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't kick the bot
        raise Exception('Cannot kick the bot')

    if permission.is_mod(member=member):
        # Don't kick moderators of the server
        raise Exception('Cannot kick moderators')

    # Kick member
    await guild.kick(member, reason=reason)

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Kicked {member.mention}** from the server',
                              colour=appearance.moderation_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    await log_message('Kick', member, moderator, guild, reason=reason)


async def ban(message: Message, member: Member, reason: str = None) -> None:
    """
    Ban member on the guild
    :param message: Message of command call
    :param member: Member to be banned
    :param reason: Reason for ban
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't ban the bot
        raise Exception('Cannot ban the bot')

    if permission.is_mod(member=member):
        # Don't ban moderators of the server
        raise Exception('Cannot ban moderators')

    # Ban member
    await guild.ban(member, reason=reason)

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Banned {member.mention}** on the server',
                              colour=appearance.moderation_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    await log_message('Ban', member, moderator, guild, reason=reason, Duration='∞')


async def tempban(message: Message, member: Member, duration_amount: int, duration_unit: str,
                  reason: str = None) -> None:
    """
    Tempban member on the guild
    :param message: Message of command call
    :param member: Member to be banned
    :param duration_amount: Duration of ban (e.g. 60)
    :param duration_unit: Unit of duration (e.g. 'minutes', 'hours')
    :param reason: Reason for ban
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't ban the bot
        raise Exception('Cannot ban the bot')

    # Don't ban moderators of the server
    if permission.is_mod(member=member):
        raise Exception('Cannot ban moderators')

    # Duration time must be positive
    if duration_amount <= 0:
        raise Exception('The duration must be positive: Invalid Duration')

    # Get correct unit & Create timedelta
    if 'minutes'.startswith(duration_unit):
        unit = 'minutes'
        tdelta: timedelta = timedelta(minutes=duration_amount)
    elif 'hours'.startswith(duration_unit):
        unit = 'hours'
        tdelta: timedelta = timedelta(hours=duration_amount)
    elif 'days'.startswith(duration_unit):
        unit = 'days'
        tdelta: timedelta = timedelta(days=duration_amount)
    elif 'weeks'.startswith(duration_unit):
        unit = 'weeks'
        tdelta: timedelta = timedelta(weeks=duration_amount)
    elif 'months'.startswith(duration_unit):
        unit = 'months'
        tdelta: timedelta = timedelta(days=duration_amount * 30)
    elif 'years'.startswith(duration_unit):
        unit = 'years'
        tdelta: timedelta = timedelta(days=duration_amount * 365)
    else:
        raise Exception('Invalid unit: Invalid Duration')

    # Don't accept duration longer than 5 years
    if tdelta > timedelta(days=5 * 365):
        raise Exception('The duration is too long: Invalid Duration')

    # Get the date, the ban expires
    until_date = datetime.utcnow() + tdelta

    # Ban member
    await guild.ban(member, reason=reason)

    # Insert ban into database
    insert.ban(temp=True, user_id=member.id, mod_id=moderator.id, date=datetime.utcnow(), guild_id=guild.id,
               reason=reason, until_date=until_date)

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Banned {member.mention}** for {duration_amount} {unit}',
                              colour=appearance.moderation_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    await log_message('Ban', member, moderator, guild, reason=reason, Duration=f'{duration_amount} {unit}')


async def check_tempban_expired(client: Client) -> None:
    """
    Handles expired temporary bans
    :param client: Bot client
    """
    expired_bans: list[Ban] = select.expired_bans()

    for ban_entry in expired_bans:
        guild: Guild = client.get_guild(ban_entry.guild_id)
        user: User = await client.fetch_user(ban_entry.user_id)
        try:
            await guild.unban(user=user, reason='Expired temporary ban')
        except Exception:
            # User could not be found, or already unbanned
            return
        delete.ban(argument=ban_entry.ban_id)
        bot_user = client.get_user(secret.bot_id)

        # Send log message in moderation log
        await log_message('Unban', user, bot_user, guild, reason='Temporary ban expired',
                          color=appearance.success_color)


async def unban(message: Message, user: str) -> None:
    """
    Unban user on the guild
    :param message: Message of command call
    :param user: Name, tag or id of user to be unbanned
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    # Try to find user by name
    ban_entry = discord.utils.find(lambda b: user == b.user.name, await guild.bans())

    # Try to finde user by ID
    if not ban_entry:
        # Check whether user is a tag
        if user.startswith('<@!') and user.endswith('>'):
            user = user[3:-1]
        ban_entry = discord.utils.find(lambda b: int(user) == b.user.id, await guild.bans())

    if not ban_entry:
        # User not banned
        raise Exception('The user is not banned')
    else:
        # User banned: Get user
        user = ban_entry.user

    # Unban user
    await guild.unban(user)

    # Delete ban out of database
    try:
        database_ban = select.Ban(guild_id=guild.id, user_id=user.id)
        delete.ban(database_ban.ban_id)
    except DatabaseEntryError:
        pass

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Unbanned {user.mention}** on the server',
                              colour=appearance.success_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    await log_message('Unban', user, moderator, guild, color=appearance.success_color, reason=None)


async def warn(message: Message, member: Member, reason: str = None) -> None:
    """
    Warn member on Guild
    :param message: Message of command execution
    :param member: Member to be warned
    :param reason: Reason for warn
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't warn the bot
        raise Exception('Cannot warn the bot')

    if permission.is_mod(member=member):
        # Don't warn moderators of the server
        raise Exception('Cannot warn moderators')

    # Insert into database
    insert.warn(user_id=member.id, mod_id=moderator.id, date=datetime.utcnow(), guild_id=guild.id, reason=reason)

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Warned {member.mention}** on the server',
                              colour=appearance.moderation_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    warn_count = select.count_warns(member.id, guild.id)

    # Send log message in moderation log
    await log_message('Warn', member, moderator, guild, reason=reason, Count=str(warn_count))

    # Warn consequence
    await warn_consequence(member)


async def warn_consequence(member: Member) -> None:
    """
    Handles consequences for warn
    :param member: Member who got banned
    """
    guild: Guild = member.guild
    bot_member: Member = guild.get_member(secret.bot_id)

    # Longterm consequence
    long_date = datetime.utcnow() - timedelta(weeks=4)
    long_warns = select.warns_date(date=long_date, after=True, guild_id=member.guild.id, user_id=member.id)

    if len(long_warns) > 3:
        # Kick and mute member
        try:
            await member.kick(reason='More than 3 warns within the last month')
        except Forbidden:
            # No permission to kick
            pass
        else:
            await log_message('Kick', member, bot_member, guild,
                              reason='More than 3 warns within the last month')
        finally:
            # Mute member for 2 hours
            until_date = datetime.utcnow() + timedelta(days=1)

            # Insert mute into database
            insert.mute(temp=True, user_id=member.id, mod_id=bot_member.id, date=datetime.utcnow(), guild_id=guild.id,
                        reason='More than 3 warns within the last month', until_date=until_date)

            # Send log message
            await log_message('Mute', member, bot_member, guild,
                              reason='More than 3 warns within the last month', Duration='1 day')
            return

    # Midterm consequence
    mid_date = datetime.utcnow() - timedelta(weeks=1)
    mid_warns = select.warns_date(date=mid_date, after=True, guild_id=member.guild.id, user_id=member.id)
    if len(mid_warns) > 2:
        # Mute member for 2 hours
        mute_role = await get_mute_role(guild)
        await member.add_roles(mute_role, reason='More than 2 warns within the last week')

        until_date = datetime.utcnow() + timedelta(hours=2)

        # Insert mute into database
        insert.mute(temp=True, user_id=member.id, mod_id=bot_member.id, date=datetime.utcnow(), guild_id=guild.id,
                    reason='More than 2 warns within the last week', until_date=until_date)

        # Send log message
        await log_message('Mute', member, bot_member, guild, reason='More than 2 warns within the last week',
                          Duration='2 hours')
        return

    # Instant consequence
    # Mute member for 30 min
    mute_role = await get_mute_role(guild)
    await member.add_roles(mute_role, reason='Warn')

    until_date = datetime.utcnow() + timedelta(minutes=30)

    # Insert mute into database
    insert.mute(temp=True, user_id=member.id, mod_id=bot_member.id, date=datetime.utcnow(), guild_id=guild.id,
                reason='Warn', until_date=until_date)

    # Send log message
    await log_message('Mute', member, bot_member, guild, reason='Warn',
                      Duration='30 minutes')


async def warns_of_member(client: Client, message: Message, member: Member) -> None:
    """
    Get a list of the warns of the member on a guild
    :param client: Bot client
    :param message: Message of command execution
    :param member: Member to get warns of
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild

    # Delete message of member
    await util.delete_message(message)

    # Get count of warns of member
    count = select.count_warns(member.id, guild.id)

    # Fetch warns
    warns: list[Warn] = select.warns_of_user(member.id, guild.id, limit=5)

    # Create embed
    desc = f'{member.mention} has **{count} warns** total.'
    if count > 0:
        desc += '\n\u200b'
    if count > 5:
        desc += '\n**Here are the latest 5 warns:**'

    embed = Embed(title=f'Warns - {member.display_name}', description=desc, colour=appearance.moderation_color)

    # Add warns to embed
    for w in warns:
        moderator: User = await client.fetch_user(w.mod_id)
        date: datetime = w.date

        if w.reason:
            embed.add_field(name=date.strftime("%Y.%m.%d"), value=f'• Moderator: {moderator.mention}'
                                                                  f'\n• Reason: {w.reason}', inline=False)
        else:
            embed.add_field(name=date.strftime("%Y.%m.%d"), value=f'• Moderator: {moderator.mention}',
                            inline=False)

    await channel.send(embed=embed)


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


async def mute(message: Message, member: Member, reason: str = None) -> None:
    """
    Mute member on the guild
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

    # Mute member
    mute_role = await get_mute_role(guild)
    await member.add_roles(mute_role, reason=reason)

    # Insert into database
    insert.mute(temp=True, user_id=member.id, mod_id=moderator.id, date=datetime.utcnow(), guild_id=guild.id,
                reason=reason)

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Muted {member.mention}** on the server',
                              colour=appearance.moderation_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    await log_message('Mute', member, moderator, guild, reason=reason, Duration='∞')


async def unmute(message: Message, member: Member) -> None:
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

    mute_role = await get_mute_role(guild)

    # Check whether the member is muted
    if not is_muted(member):
        raise Exception('Member is not muted')

    # Remove mute role
    await member.remove_roles(mute_role, reason=f'Unmute by {moderator.display_name}')

    # Delete mute out of database
    try:
        database_mute = select.Mute(guild_id=guild.id, user_id=member.id)
        delete.ban(database_mute.mute_id)
    except DatabaseEntryError:
        pass

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Unmuted {member.mention}** on the server',
                              colour=appearance.success_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    await log_message('Unmute', member, moderator, guild, color=appearance.success_color, reason=None)


async def tempmute(message: Message, member: Member, duration_amount: int, duration_unit: str,
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
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't mute the bot
        raise Exception('Cannot mute the bot')

    # Don't mute moderators of the server
    if permission.is_mod(member=member):
        raise Exception('Cannot mute moderators')

    # Duration time must be positive
    if duration_amount <= 0:
        raise Exception('The duration must be positive: Invalid Duration')

    # Get correct unit & Create timedelta
    if 'minutes'.startswith(duration_unit):
        unit = 'minutes'
        tdelta: timedelta = timedelta(minutes=duration_amount)
    elif 'hours'.startswith(duration_unit):
        unit = 'hours'
        tdelta: timedelta = timedelta(hours=duration_amount)
    elif 'days'.startswith(duration_unit):
        unit = 'days'
        tdelta: timedelta = timedelta(days=duration_amount)
    elif 'weeks'.startswith(duration_unit):
        unit = 'weeks'
        tdelta: timedelta = timedelta(weeks=duration_amount)
    elif 'months'.startswith(duration_unit):
        unit = 'months'
        tdelta: timedelta = timedelta(days=duration_amount * 30)
    elif 'years'.startswith(duration_unit):
        unit = 'years'
        tdelta: timedelta = timedelta(days=duration_amount * 365)
    else:
        raise Exception('Invalid unit: Invalid Duration')

    # Don't accept duration longer than 5 years
    if tdelta > timedelta(days=5 * 365):
        raise Exception('The duration is too long: Invalid Duration')

    # Get the date, the ban expires
    until_date = datetime.utcnow() + tdelta

    # Mute member
    mute_role = await get_mute_role(guild)
    await member.add_roles(mute_role, reason=reason)

    # Insert mute into database
    insert.mute(temp=True, user_id=member.id, mod_id=moderator.id, date=datetime.utcnow(), guild_id=guild.id,
                reason=reason, until_date=until_date)

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Muted {member.mention}** for {duration_amount} {unit}',
                              colour=appearance.moderation_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    await log_message('Mute', member, moderator, guild, reason=reason, Duration=f'{duration_amount} {unit}')


async def check_tempmute_expired(client: Client) -> None:
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
        mute_role = await get_mute_role(guild)
        bot_user = client.user

        # Remove mute role from member
        if member:
            await member.remove_roles(mute_role, reason=f'Temporar ban expired')

            # Send log message in moderation log
            await log_message('Unmute', member, bot_user, guild, reason='Temporary mute expired',
                              color=appearance.success_color)

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


async def report(message: Message, member: Member, reason: str) -> None:
    """
    Report a member
    :param message: Message of command execution
    :param member: Member to be reported
    :param reason: Reason for report
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    reported_by: Member = message.author
    mod_log = get_mod_log(guild)

    if not mod_log:
        # Ignore if the moderation log is not set up
        raise Exception('Moderation log must be set up')

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't warn the bot
        raise Exception('Cannot report the bot')

    if permission.is_mod(member=member):
        # Don't warn moderators of the server
        raise Exception('Cannot report moderators')

    # Insert into database
    insert.report(reporter_id=reported_by.id, user_id=member.id, date=datetime.utcnow(), guild_id=guild.id,
                  reason=reason)

    # Send embed as response in chat
    chat_embed: Embed = Embed(description=f'**Reported {member.mention}**',
                              colour=appearance.moderation_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    log_embed: Embed = Embed(colour=appearance.moderation_color, timestamp=datetime.utcnow())

    # Add fields
    log_embed.set_author(name='Report', icon_url=member.avatar_url)
    log_embed.set_footer(text=reported_by.display_name, icon_url=reported_by.avatar_url)

    log_embed.add_field(name='User', value=member.mention, inline=True)
    log_embed.add_field(name='Reported by', value=reported_by.mention, inline=True)

    log_embed.add_field(name='Reason', value=reason, inline=False)

    await mod_log.send(embed=log_embed)


async def reports_of_member(client: Client, message: Message, member: Member) -> None:
    """
    Get a list of the reports of the member on a guild
    :param client: Bot client
    :param message: Message of command execution
    :param member: Member to get reports of
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    mod_log = get_mod_log(guild)

    if not mod_log:
        # Ignore if the moderation log is not set up
        raise Exception('Moderation log must be set up')

    # Delete message of member
    await util.delete_message(message)

    # Get count of warns of member
    count = select.count_reports(member.id, guild.id)

    # Fetch warns
    reports: list[Report] = select.reports_of_user(member.id, guild.id, limit=5)

    # Create embed
    desc = f'{member.mention} has **{count} reports** total.'
    if count > 0:
        desc += '\n\u200b'
    if count > 5:
        desc += '\n**Here are the latest 5 reports:**'

    embed = Embed(title=f'Reports - {member.display_name}', description=desc, colour=appearance.moderation_color)

    # Add reports to embed
    for r in reports:
        reported_by: User = await client.fetch_user(r.reporter_id)
        date: datetime = r.date

        embed.add_field(name=date.strftime("%Y.%m.%d"), value=f'• Moderator: {reported_by.mention}'
                                                              f'\n• Reason: {r.reason}', inline=False)

    await channel.send(embed=embed)
