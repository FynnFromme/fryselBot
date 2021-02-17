from fryselBot.utilities import permission, style, secret
from fryselBot.commands import description
from discord import Message, Guild, Member, TextChannel, Embed


async def response(message: Message) -> None:
    """
    Sends help messages.
    :param message: Message that executed the command
    :return: None
    """
    # Initialize attributes of message
    member: Member = message.author

    # Call different help messages depending on permission
    await _member_help(message)

    if permission.is_admin(member):
        await _mod_help(message, footer=False)
        await _admin_help(message)
    elif permission.is_mod(member):
        await _mod_help(message)

    # Delete message
    await message.delete()


async def _member_help(message: Message) -> None:
    """
    Sends help message for members in the text channel.
    :param message: Message that executed the command
    :return: None
    """

    # Initialize attributes of message
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    member: Member = message.author

    prefix = style.get_prefix(guild.id)

    # Setup embed content
    embed: Embed = Embed()
    embed.title = "Commands - " + style.bot_name

    # Add fields for commands
    for cmd, desc in description.member_commands.items():
        embed.add_field(name="`" + prefix + cmd + "`", value=desc, inline=False)

    # Add fields for other bot functions
    for func, desc in description.member_functions.items():
        embed.add_field(name="`" + func + "`", value=desc, inline=False)

    # Setup embed style
    embed.colour = style.get_primary_color(guild.id)
    embed.set_thumbnail(url=guild.get_member(secret.bot_id).avatar_url)
    embed.set_footer(text="Created by frysel | []-Required | ()-Optional", icon_url=member.avatar_url)

    # Send message
    await channel.send(embed=embed)


async def _mod_help(message: Message, footer: bool = True) -> None:
    """
    Sends help message for moderators via dm.
    :param message: Message that executed the command
    :param footer: Whether the embed should have a footer
    :return: None
    """
    # Initialize attributes of message
    guild: Guild = message.guild
    member: Member = message.author

    prefix = style.get_prefix(guild.id)

    # Setup embed content
    embed: Embed = Embed()
    embed.title = "Moderator Commands"

    # Add fields for commands
    for cmd, desc in description.moderator_commands.items():
        embed.add_field(name="`" + prefix + cmd + "`", value=desc, inline=False)

    # Setup embed style
    embed.colour = style.get_primary_color(guild.id)

    if footer:
        embed.set_footer(text="Created by frysel | []-Required | ()-Optional", icon_url=member.avatar_url)

    # Send message
    await member.send(embed=embed)


async def _admin_help(message: Message) -> None:
    """
    Sends help message for admins via dm.
    :return: None
    """
    # Initialize attributes of message
    guild: Guild = message.guild
    member: Member = message.author

    prefix = style.get_prefix(guild.id)

    # Setup embed content
    embed: Embed = Embed()
    embed.title = "Admin Commands"

    # Add fields for commands
    for cmd, desc in description.admin_commands.items():
        embed.add_field(name="`" + prefix + cmd + "`", value=desc, inline=False)

    # Add fields for other bot functions
    for func, desc in description.admin_functions.items():
        embed.add_field(name="`" + func + "`", value=desc, inline=False)

    # Setup embed style
    embed.colour = style.get_primary_color(guild.id)
    embed.set_footer(text="Created by frysel | []-Required | ()-Optional", icon_url=member.avatar_url)

    # Send message
    await member.send(embed=embed)
