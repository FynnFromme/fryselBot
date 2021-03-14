from discord import Message, Member, TextChannel, Guild, Embed, Client, User
from datetime import datetime

from fryselBot.database.select import Report
from fryselBot.utilities import util, secret
from fryselBot.system import permission, appearance
from fryselBot.system.moderation import moderation
from fryselBot.database import insert, select


async def report_cmd(message: Message, member: Member, reason: str) -> None:
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
    mod_log = moderation.get_mod_log(guild)

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
    await moderation.chat_message(channel, f'Reported {member.mention} for {reason}', appearance.moderation_color,
                                  reported_by)

    # Send log message in moderation log
    log_embed: Embed = Embed(colour=appearance.moderation_color, timestamp=datetime.utcnow())

    # Add fields
    log_embed.set_author(name='Report', icon_url=member.avatar_url)
    log_embed.set_footer(text=reported_by.display_name, icon_url=reported_by.avatar_url)

    log_embed.add_field(name='User', value=member.mention, inline=True)
    log_embed.add_field(name='Reported by', value=reported_by.mention, inline=True)

    log_embed.add_field(name='Channel', value=channel.mention, inline=True)

    log_embed.add_field(name='Reason', value=reason, inline=False)

    await mod_log.send(embed=log_embed)


async def reports_of_member_cmd(client: Client, message: Message, member: Member) -> None:
    """
    Get a list of the reports of the member on a guild
    :param client: Bot client
    :param message: Message of command execution
    :param member: Member to get reports of
    """
    # Initialize varaibles
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    mod_log = moderation.get_mod_log(guild)

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
