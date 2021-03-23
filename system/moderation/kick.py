from discord import Message, Member, TextChannel, Guild, Client
from system import appearance, permission
from utilities import util, secret
from system.moderation import moderation


async def kick(member: Member, moderator: Member, client: Client, reason: str = None) -> None:
    """
    Kick member from guild and send log message
    :param member: Member to kick
    :param moderator: Moderator of kick
    :param client: Bot client
    :param reason: Reason for kick
    """
    guild: Guild = member.guild

    # Send private message
    if permission.ban_kick_member(client, member):
        await moderation.private_message(member, f'You got kicked from {guild.name}', None, moderator, Reason=reason)

    # Kick member
    await guild.kick(member, reason=reason)

    # Send log message in moderation log
    await moderation.log_message('Kick', member, moderator, guild, reason=reason)


async def kick_cmd(message: Message, member: Member, client: Client, reason: str = None) -> None:
    """
    Kick command
    :param message: Message of command call
    :param member: Member to be kicked
    :param client: bot client
    :param reason: Reason for kick
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't kick the bot
        raise Exception('Cannot kick the bot')

    if permission.is_mod(member=member):
        # Don't kick moderators of the server
        raise Exception('Cannot kick moderators')

    # Kick member and send log message
    await kick(member, moderator, client, reason)

    # Send embed as response in chat
    await moderation.chat_message(channel, f'Kicked {member.mention}', appearance.moderation_color, moderator)
