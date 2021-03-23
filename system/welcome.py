from database import update, select
from system import description, appearance
from utilities import secret, util
from discord import Member, Guild, TextChannel, Embed, Forbidden
import random


async def welcome_message(member: Member) -> None:
    """
    Sends welcome message for member
    :param member: Member joined
    """
    guild: Guild = member.guild

    if not select.welcome_messages(guild.id):
        # Only send welcome messages when they are enabled on guild
        return

    # Get welcome channel
    welcome_channel: TextChannel = guild.get_channel(select.welcome_channel_id(guild.id))

    welcome_messages = ['{} joined. You must construct additional pylons.',
                        'Never gonna give {} up. Never let {} down!',
                        'Hey! Listen! {} has joined!',
                        'Ha! {} has joined! You activated my trap card!',
                        "We've been expecting you, {}.",
                        "It's dangerous to go alone, take {}!",
                        'Swoooosh. {} just landed.',
                        'Brace yourselves. {} just joined the Server.',
                        'A wild {} appeared.'
                        ]

    # Setup embed
    embed: Embed = Embed()
    embed.description = random.choice(welcome_messages).replace('{}', member.mention)

    # Setup embed style
    embed.colour = appearance.get_color(guild.id)

    # Send embed to welcome_channel
    await welcome_channel.send(embed=embed)


async def leave_message(member: Member) -> None:
    """
    Sends leave message for member
    :param member: Member left
    """
    guild: Guild = member.guild

    if not select.leave_messages(guild.id):
        # Only send leave messages when they are enabled on guild
        return

    # Get welcome channel
    welcome_channel: TextChannel = guild.get_channel(select.welcome_channel_id(guild.id))

    welcome_messages = ["{} left, the party's over."]

    # Setup embed
    embed: Embed = Embed()
    embed.description = random.choice(welcome_messages).replace('{}', member.mention)

    # Setup embed style
    embed.colour = appearance.get_color(guild.id)

    # Send embed to welcome_channel
    await welcome_channel.send(embed=embed)


def toggle_welcome(guild: Guild, disable: bool = False) -> None:
    """
    Toggles welcome messages on the guild.
    :param guild: Guild ID to toggle welcome messages
    :param disable: Force to disable leave messages
    :raises Exception: if welcome messages are being enabled and the welcome channel is not set up
    """
    if select.welcome_messages(guild.id) or disable:
        update.welcome_messages(argument=guild.id, value=False)
    else:
        if not select.welcome_channel_id:
            raise Exception('Welcome Channel is not set up')
        else:
            update.welcome_messages(argument=guild.id, value=True)


def toggle_leave(guild: Guild, disable: bool = False) -> None:
    """
    Toggles leave messages on the guild.
    :param guild: Guild ID to toggle leave messages
    :param disable: Force to disable leave messages
    :raises Exception: if leave messages are being enabled and the welcome channel is not set up
    """
    if select.leave_messages(guild.id) or disable:
        update.leave_messages(argument=guild.id, value=False)
    else:
        if not select.welcome_channel_id:
            raise Exception('Welcome Channel is not set up')
        else:
            update.leave_messages(argument=guild.id, value=True)


def set_welcome_channel(guild: Guild, channel_id: int = None) -> None:
    """
    Sets the welcome channel for a guild
    :param guild: Guild to set the welcome channel for
    :param channel_id: ChannelID which becomes the welcome channel
    :raises InvalidInputError: if channel_id exists not on the guild
    """
    if channel_id:
        # Check whether the channel is a channel on the guild
        channel_ids = list(map(lambda c: c.id, guild.channels))
        if channel_id not in channel_ids:
            # channel_id isn't on the guild
            raise util.InvalidInputError(channel_id, "The given channel isn't a channel on the guild")

    # Set the channel to the welcome_channel
    update.welcome_channel_id(argument=guild.id, value=channel_id)


async def welcome_dm(member: Member, channel: TextChannel = None, force: bool = False):
    """
    Welcome members to the server via DM
    :param member: Member to welcome
    :param channel: Channel of call
    :param force: Force the dm without checking whether they are enabled
    """
    guild: Guild = member.guild

    if not select.welcome_dms(guild.id) and not force:
        # Only send welcome dms when they are enabled on guild
        return

    # Set welcome text
    text: str = select.welcome_dm(guild.id)
    # Replace <member> with the name of the member
    text = text.replace('<member>', member.display_name)

    # Setup embed
    embed: Embed = Embed(title=f'Welcome to {guild.name}!', description=text, color=appearance.get_color(guild.id))

    embed.set_thumbnail(url=guild.icon_url)
    embed.set_footer(text=f'Use {appearance.get_prefix(guild.id)}help on {guild.name}',
                     icon_url=guild.get_member(secret.bot_id).avatar_url)

    # Send direct message or in channel if dm is forbidden
    try:
        await member.send(embed=embed)
    except Forbidden:
        if channel and force:
            await channel.send(embed=embed)


def toggle_welcome_dm(guild: Guild, disable: bool = False) -> None:
    """
    Toggles welcome dms on the guild.
    :param guild: Guild ID to toggle welcome messages
    :param disable: Force to disable leave messages
    :raises Exception: if welcome messages are being enabled and the welcome channel is not set up
    """
    if select.welcome_dms(guild.id) or disable:
        update.welcome_dms(argument=guild.id, value=False)
    else:
        if not select.welcome_dm:
            raise Exception('Welcome dm text is not set up')
        else:
            update.welcome_dms(argument=guild.id, value=True)


def set_welcome_dm(guild: Guild, text: str = None) -> None:
    """
    Sets the welcome channel for a guild
    :param guild: Guild to set the welcome channel for
    :param text: The message, new members get via dm
    """

    # Set the channel to the welcome_channel
    update.welcome_dm(argument=guild.id, value=text)
