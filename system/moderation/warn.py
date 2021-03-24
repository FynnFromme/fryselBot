from discord import Message, Member, TextChannel, Guild, Embed, Forbidden, Client, User
from datetime import datetime, timedelta

from database.select import Warn
from utilities import util, secret
from system import permission, appearance
from system.moderation import moderation, mute, kick
from database import select, insert


async def warn(member: Member, moderator: Member, reason: str = None) -> None:
    """
    Warn memeber
    :param member: Member to warn
    :param moderator: Moderator of warn
    :param reason: Reason for warn
    """
    guild: Guild = member.guild

    # Insert into database
    insert.warn(user_id=member.id, mod_id=moderator.id, date=datetime.utcnow(), guild_id=guild.id, reason=reason)

    warn_count = select.count_warns(member.id, guild.id)

    # Send private message
    await moderation.private_message(member, f'You got warned on {guild.name}', None, moderator, Count=warn_count,
                                     Reason=reason)

    # Send log message in moderation log
    await moderation.log_message('Warn', member, moderator, guild, reason=reason, Count=str(warn_count))

    # Warn consequence
    await warn_consequence(member)


async def warn_cmd(message: Message, member: Member, reason: str = None) -> None:
    """
    Warn command
    :param message: Message of command execution
    :param member: Member to be warned
    :param reason: Reason for warn
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    moderator: Member = message.author

    # Delete message of member
    await util.delete_message(message)

    if member.id == secret.bot_id:
        # Don't warn the bot
        raise Exception('Cannot warn the bot')

    if permission.is_mod(member=member):
        # Don't warn moderators of the server
        raise Exception('Cannot warn moderators')

    await warn(member, moderator, reason)

    # Send embed as response in chat
    await moderation.chat_message(channel, f'Warned {member.mention}', appearance.moderation_color, moderator)


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
            await kick.kick(member, bot_member, reason='More than 3 warns within the last month')
        except Forbidden:
            # No permission to kick
            pass
        finally:
            # Tempmute member
            await mute.tempmute(member, bot_member, '1 day', timedelta(days=1),
                                'More than 3 warns within the last month')
            return

    # Midterm consequence
    mid_date = datetime.utcnow() - timedelta(weeks=1)
    mid_warns = select.warns_date(date=mid_date, after=True, guild_id=member.guild.id, user_id=member.id)
    if len(mid_warns) > 2:
        # Mute member for 2 hours
        await mute.tempmute(member, bot_member, '2 hours', timedelta(hours=2),
                            'More than 2 warns within the last week')
        return

    # Instant consequence
    # Mute member for 20 min
    await mute.tempmute(member, bot_member, '20 minutes', timedelta(minutes=20),
                        'Warn')


async def warns_of_member_cmd(client: Client, message: Message, member: Member) -> None:
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
    
