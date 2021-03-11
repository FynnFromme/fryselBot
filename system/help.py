from fryselBot.utilities import permission, secret, util
from fryselBot.system import description, appearance
from discord import Message, Guild, Member, TextChannel, Embed, Forbidden


async def cmd_help(message: Message, cmd_name: str) -> None:
    """
    Sends help to a command
    :param message: Message that executed the command
    :param cmd_name: Name of the command
    """
    # Initialize varaibles
    guild: Guild = message.guild
    channel: TextChannel = message.channel
    prefix = appearance.get_prefix(guild.id)

    # Call different help messages depending on permission
    is_suggestion, similar_cmd = description.get_similar_command(cmd_name)

    # Get name with first letter in upper
    name = similar_cmd.name[0].upper() + similar_cmd.name[1:]

    if not is_suggestion:
        embed = Embed(title=f'Help - {name}', description=f'`{prefix}{similar_cmd.syntax}`\n'
                                                          f'{similar_cmd.get_complete_description()}',
                      colour=appearance.get_color(guild.id))
    else:
        embed = Embed(title=f'Help - {name}', description=f'**Did you mean {similar_cmd.name}?**\n\n'
                                                          f'`{prefix}{similar_cmd.syntax}`\n'
                                                          f'{similar_cmd.get_complete_description()}',
                      colour=appearance.get_color(guild.id))

    embed.set_footer(text='Created by frysel  |  <> Required  |  () Optional', icon_url=message.author.avatar_url)
    await channel.send(embed=embed)

    # Delete message
    await util.delete_message(message)


async def help_command(message: Message) -> None:
    """
    Sends help messages.
    :param message: Message that executed the command
    """
    # Initialize attributes of message
    member: Member = message.author

    # Call different help messages depending on permission
    await _member_help(message)

    if permission.is_admin(member=member):
        await _mod_help(message, message.channel, footer=False)
        await _admin_help(message, message.channel)

    elif permission.is_mod(member=member):
        await _mod_help(message, message.channel)

    # Delete message
    await util.delete_message(message)


async def _member_help(message: Message) -> None:
    """
    Sends help message for members in the text channel.
    :param message: Message that executed the command
    """

    # Initialize attributes of message
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    member: Member = message.author

    prefix = appearance.get_prefix(guild.id)

    # Setup embed content
    embed: Embed = Embed()
    embed.title = 'Commands - ' + appearance.bot_name

    # Add fields for commands
    for cmd in description.commands:
        if cmd.member_cmd() and cmd.in_help:
            embed.add_field(name='`' + prefix + cmd.syntax + '`', value=cmd.get_complete_description(), inline=False)

    # Add fields for other bot functions
    for func in description.functions:
        embed.add_field(name='`' + func.name + '`', value=func.description, inline=False)

    # Setup embed style
    embed.colour = appearance.get_color(guild.id)
    embed.set_thumbnail(url=guild.get_member(secret.bot_id).avatar_url)
    embed.set_footer(text='Created by frysel  |  <> Required  |  () Optional', icon_url=member.avatar_url)

    # Send message
    await channel.send(embed=embed)


async def _mod_help(message: Message, channel: TextChannel, footer: bool = True) -> None:
    """
    Sends help message for moderators via dm.
    :param message: Message that executed the command
    :param footer: Whether the embed should have a footer
    """
    # Initialize attributes of message
    guild: Guild = message.guild
    member: Member = message.author

    prefix = appearance.get_prefix(guild.id)

    # Setup embed content
    embed: Embed = Embed()
    embed.title = 'Moderator Commands'

    # Add fields for commands
    for cmd in description.commands:
        if cmd.mod_only and cmd.in_help:
            embed.add_field(name='`' + prefix + cmd.syntax + '`', value=cmd.get_complete_description(), inline=False)

    # Setup embed style
    embed.colour = appearance.get_color(guild.id)

    if footer:
        embed.set_footer(text='Created by frysel  |  <> Required  |  () Optional', icon_url=member.avatar_url)

    # Send direct message or in channel if dm is forbidden
    try:
        await member.send(embed=embed)
    except Forbidden:
        await channel.send(embed=embed)


async def _admin_help(message: Message, channel: TextChannel) -> None:
    """
    Sends help message for admins via dm.
    :return: None
    """
    # Initialize attributes of message
    guild: Guild = message.guild
    member: Member = message.author

    prefix = appearance.get_prefix(guild.id)

    # Setup embed content
    embed: Embed = Embed()
    embed.title = 'Admin Commands'

    # Add fields for commands
    for cmd in description.commands:
        if cmd.admin_only and cmd.in_help:
            embed.add_field(name='`' + prefix + cmd.syntax + '`', value=cmd.get_complete_description(), inline=False)

    # Add fields for other bot functions
    for func in description.functions:
        embed.add_field(name='`' + func.name + '`', value=func.description, inline=False)

    # Setup embed style
    embed.colour = appearance.get_color(guild.id)
    embed.set_footer(text='Created by frysel  |  <> Required  |  () Optional', icon_url=member.avatar_url)

    # Send direct message or in channel if dm is forbidden
    try:
        await member.send(embed=embed)
    except Forbidden:
        await channel.send(embed=embed)
