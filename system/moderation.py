from datetime import datetime, timedelta

import discord
from discord import TextChannel, Member, Embed, Guild, User, Client, Message

from fryselBot.database._manager import DatabaseEntryError
from fryselBot.database.select import Ban, Warn
from fryselBot.system import appearance
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
    mod_log: TextChannel = get_mod_log(guild)
    if mod_log:
        # Create embed and set up style
        log_embed: Embed = Embed(colour=appearance.moderation_color, timestamp=datetime.utcnow())

        log_embed.set_author(name='Kick', icon_url=member.avatar_url)
        log_embed.set_footer(text=moderator.display_name, icon_url=moderator.avatar_url)

        log_embed.add_field(name='User', value=member.mention, inline=True)
        log_embed.add_field(name='Moderator', value=moderator.mention, inline=True)

        # Add reason in case it was given
        if reason:
            log_embed.add_field(name='Reason', value=reason, inline=False)

        await mod_log.send(embed=log_embed)


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
    mod_log: TextChannel = get_mod_log(guild)
    if mod_log:
        # Create embed and set up style
        log_embed: Embed = Embed(colour=appearance.moderation_color, timestamp=datetime.utcnow())

        log_embed.set_author(name='Ban', icon_url=member.avatar_url)
        log_embed.set_footer(text=moderator.display_name, icon_url=moderator.avatar_url)

        log_embed.add_field(name='User', value=member.mention, inline=True)
        log_embed.add_field(name='Moderator', value=moderator.mention, inline=True)
        log_embed.add_field(name='Duration', value='∞')

        # Add reason in case it was given
        if reason:
            log_embed.add_field(name='Reason', value=reason, inline=False)

        await mod_log.send(embed=log_embed)


async def tempban(message: Message, member: Member, duration_amount: int, duration_unit: str,
                  reason: str = None) -> None:
    """
    Ban member on the guild
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
        # Don't kick the bot
        raise Exception('Cannot ban the bot')

    # Don't kick moderators of the server
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
    mod_log: TextChannel = get_mod_log(guild)
    if mod_log:
        # Create embed and set up style
        log_embed: Embed = Embed(colour=appearance.moderation_color, timestamp=datetime.utcnow())

        log_embed.set_author(name='Ban', icon_url=member.avatar_url)
        log_embed.set_footer(text=moderator.display_name, icon_url=moderator.avatar_url)

        log_embed.add_field(name='User', value=member.mention, inline=True)
        log_embed.add_field(name='Moderator', value=moderator.mention, inline=True)
        log_embed.add_field(name='Duration', value=f'{duration_amount} {unit}')

        # Add reason in case it was given
        if reason:
            log_embed.add_field(name='Reason', value=reason, inline=False)

        await mod_log.send(embed=log_embed)


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
        mod_log: TextChannel = get_mod_log(guild)
        if mod_log:
            # Create embed and set up style
            log_embed: Embed = Embed(colour=appearance.success_color, timestamp=datetime.utcnow())

            log_embed.set_author(name='Unban', icon_url=user.avatar_url)
            log_embed.set_footer(text=bot_user.display_name, icon_url=bot_user.avatar_url)

            log_embed.add_field(name='User', value=user.mention, inline=True)
            log_embed.add_field(name='Moderator', value=bot_user.mention, inline=True)
            log_embed.add_field(name='Reason', value='Temporary ban expired', inline=False)

            await mod_log.send(embed=log_embed)


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
                              colour=appearance.moderation_color)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=10)

    # Send log message in moderation log
    mod_log: TextChannel = get_mod_log(guild)
    if mod_log:
        # Create embed and set up style
        log_embed: Embed = Embed(colour=appearance.success_color, timestamp=datetime.utcnow())

        log_embed.set_author(name='Unban', icon_url=user.avatar_url)
        log_embed.set_footer(text=moderator.display_name, icon_url=moderator.avatar_url)

        log_embed.add_field(name='User', value=user.mention, inline=True)
        log_embed.add_field(name='Moderator', value=moderator.mention, inline=True)

        await mod_log.send(embed=log_embed)


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

    # Send log message in moderation log
    mod_log: TextChannel = get_mod_log(guild)
    if mod_log:
        # Create embed and set up style
        log_embed: Embed = Embed(colour=appearance.moderation_color, timestamp=datetime.utcnow())

        log_embed.set_author(name='Warn', icon_url=member.avatar_url)
        log_embed.set_footer(text=moderator.display_name, icon_url=moderator.avatar_url)

        log_embed.add_field(name='User', value=member.mention, inline=True)
        log_embed.add_field(name='Moderator', value=moderator.mention, inline=True)

        log_embed.add_field(name='Count', value=str(select.count_warns(member.id, guild.id)), inline=True)

        # Add reason in case it was given
        if reason:
            log_embed.add_field(name='Reason', value=reason, inline=False)

        await mod_log.send(embed=log_embed)


async def warns_of_member(client: Client, message: Message, member: Member) -> None:
    """

    :param client:
    :param message:
    :param member:
    :return:
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    count = select.count_warns(member.id, guild.id)

    if count == 0:
        # No warns
        return

    # Fetch warns
    warns: list[Warn] = select.warns_of_user(member.id, guild.id, limit=10)

    embed = Embed(title=f'Warns - {member.display_name}',
                  description=f'{member.display_name} has **{count} warns total.**',
                  colour=appearance.moderation_color)

    for w in warns:
        if w.reason:
            embed.add_field(name=f'Warn - {w.date}', value=f'• **Moderator:** {await client.fetch_user(moderator.id)}'
                                                           f'\n• **Reason:** {w.reason}', inline=False)
        else:
            embed.add_field(name=f'Warn - {w.date}', value=f'• **Moderator:** {await client.fetch_user(moderator.id)}',
                            inline=False)

    await channel.send(embed=embed)
