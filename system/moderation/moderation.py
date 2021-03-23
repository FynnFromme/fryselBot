from datetime import datetime, timedelta
from typing import Union

from discord import TextChannel, Member, Embed, Guild, User, Forbidden

from database import update, select
from system import appearance


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


async def chat_message(channel: TextChannel, text: str, color: hex, moderator: Member = None) -> None:
    """
    Send message in chat and delete it after 10 seconds
    :param channel: Channel to send message
    :param text: Text of emebd
    :param color: Color of embed
    :param moderator: Moderator of operation (added to footer)
    """
    # Send embed as response in chat
    chat_embed: Embed = Embed(description=text, colour=color)

    if moderator:
        chat_embed.set_footer(text=f'by {moderator.display_name}', icon_url=moderator.avatar_url)

    chat_msg = await channel.send(embed=chat_embed)
    await chat_msg.delete(delay=15)


async def private_message(member: Member, title: str = None, description: str = None, moderator: Member = None,
                          color: hex = appearance.moderation_color, **kwargs) -> None:
    """
    Send message in chat and delete it after 10 seconds
    :param member: Member to send message to
    :param title: Title of embed
    :param description: Description of embed
    :param moderator: Moderator of operation (added to footer)
    :param color: Color of embed
    :param kwargs: Fields
    """
    # Create embed
    embed: Embed = Embed(title=title, description=description, colour=color)

    # Add moderator to footer
    if moderator:
        embed.set_footer(text=f'by {moderator.display_name}', icon_url=moderator.avatar_url)

    # Add fields
    for name, value in kwargs.items():
        if value:
            embed.add_field(name=name, value=value)

    # Try to send embed
    try:
        await member.send(embed=embed)
    except Forbidden:
        pass


def get_duration(duration_amount: int, duration_unit: str) -> tuple[timedelta, str]:
    """
    Retrieves timedelta and string representation out of parameters
    :param duration_amount: Amount as string
    :param duration_unit: Unit as strings
    """
    duration_amount = int(duration_amount)

    # Duration time must be positive
    if duration_amount <= 0:
        raise Exception('The duration must be a positive integer: Invalid Duration')

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

    return tdelta, f'{duration_amount} {unit}'
