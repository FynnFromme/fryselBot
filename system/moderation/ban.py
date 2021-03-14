from datetime import timedelta, datetime
from discord import Message, Member, TextChannel, Guild, User, Client, utils as dc_utils

from fryselBot.database import delete, select, insert
from fryselBot.database.select import Ban
from fryselBot.utilities import util, secret
from fryselBot.system import permission, appearance
from fryselBot.system.moderation import moderation


async def ban(member: Member, moderator: Member, client: Client, reason: str = None) -> None:
    """
    Ban member on guild and send log message
    :param member: Member to ban
    :param moderator: Moderator of ban
    :param client: Bot client
    :param reason: Reason for ban
    """
    guild: Guild = member.guild

    # Delete old entries out of database
    delete.bans_of_member(user_id=member.id, guild_id=guild.id)

    # Send private message
    if permission.ban_kick_member(client, member):
        await moderation.private_message(member, f'You got banned from {guild.name}', None, moderator, Reason=reason)

    # Ban member
    await guild.ban(member, reason=reason)

    # Send log message in moderation log
    await moderation.log_message('Ban', member, moderator, guild, reason=reason, Duration='∞')


async def ban_cmd(message: Message, member: Member, client: Client, reason: str = None) -> None:
    """
    Ban command
    :param message: Message of command call
    :param member: Member to be banned
    :param client: Bot client
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

    # Ban member and send log message
    await ban(member, moderator, client, reason)

    # Send embed as response in chat
    await moderation.chat_message(channel, f'Banned {member.mention}', appearance.moderation_color,
                                  moderator)


async def tempban(member: Member, moderator: Member, duration: str, tdelta: timedelta, client: Client,
                  reason: str = None) -> None:
    """
    Tempban member and send log message
    :param member: Member to ban
    :param moderator: Moderator of ban
    :param duration: String represenation of timedelta
    :param tdelta: Timedelta of tempban
    :param client: Bot client
    :param reason: Reason for ban
    """
    guild: Guild = member.guild

    # Get the date, the mute expires
    until_date = datetime.utcnow() + tdelta

    # Send private message
    if permission.ban_kick_member(client, member):
        await moderation.private_message(member, f'You got banned from {guild.name}', None, moderator,
                                         Duration=duration, Reason=reason)

    # Ban member
    await guild.ban(member, reason=reason)

    # Delete old entries out of database
    delete.bans_of_member(user_id=member.id, guild_id=guild.id)

    # Insert ban into database
    insert.ban(temp=True, user_id=member.id, mod_id=moderator.id, date=datetime.utcnow(), guild_id=guild.id,
               reason=reason, until_date=until_date)

    # Send log message in moderation log
    await moderation.log_message('Ban', member, moderator, guild, reason=reason, Duration=duration)


async def tempban_cmd(message: Message, member: Member, duration_amount: int, duration_unit: str, client: Client,
                      reason: str = None) -> None:
    """
    Tempban member on the guild
    :param message: Message of command call
    :param member: Member to be banned
    :param duration_amount: Duration of ban (e.g. 60)
    :param duration_unit: Unit of duration (e.g. 'minutes', 'hours')
    :param client: Bot client
    :param reason: Reason for ban
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't ban the bot
        raise Exception('Cannot ban the bot')

    # Don't ban moderators of the server
    if permission.is_mod(member=member):
        raise Exception('Cannot ban moderators')

    tdelta, duration = moderation.get_duration(duration_amount, duration_unit)

    # Mute member and send log message
    await tempban(member, moderator, duration, tdelta, client, reason)

    # Send embed as response in chat
    await moderation.chat_message(channel, f'Banned {member.mention} for {duration}', appearance.moderation_color,
                                  moderator)


async def check_expired(client: Client) -> None:
    """
    Handles expired temporary bans
    :param client: Bot client
    """
    expired_bans: list[Ban] = select.expired_bans()

    for ban_entry in expired_bans:
        user: User = await client.fetch_user(ban_entry.user_id)
        bot_user = client.get_user(secret.bot_id)

        # Try unban user and send log message
        await unban(user, bot_user, 'Temporary ban expired')


async def unban(user: User, moderator: Member, reason: str = None) -> None:
    """
    Unban user and send log message
    :param user: User to unban
    :param moderator: Moderator of unban
    :param reason: Reason for unban
    """

    guild: Guild = moderator.guild
    # Try to unban user
    try:
        await guild.unban(user, reason=reason)
    except Exception:
        pass

    # Delete ban entries out of database
    delete.bans_of_member(user_id=user.id, guild_id=guild.id)

    # Send log message in moderation log
    await moderation.log_message('Unban', user, moderator, guild, color=appearance.success_color, reason=reason)


async def unban_cmd(message: Message, user: str) -> None:
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
    ban_entry = dc_utils.find(lambda b: user == b.user.name, await guild.bans())

    # Try to finde user by ID
    if not ban_entry:
        # Check whether user is a tag
        if user.startswith('<@!') and user.endswith('>'):
            user = user[3:-1]
        ban_entry = dc_utils.find(lambda b: int(user) == b.user.id, await guild.bans())

    if not ban_entry:
        # User not banned
        raise Exception('The user is not banned')
    else:
        # User banned: Get user
        user = ban_entry.user

    # Unban user and send log message
    await unban(user, moderator)

    # Send embed as response in chat
    await moderation.chat_message(channel, f'Unbanned {user.mention}', appearance.success_color,
                                  moderator)
