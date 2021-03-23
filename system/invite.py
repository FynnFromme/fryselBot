from system import appearance
from discord import Message, Guild, Member, TextChannel, Embed, Invite


async def invite_command(message: Message) -> None:
    """
    Sends server invite messages.
    :param message: Message that executed the command
    :return: None
    """
    # Initialize attributes of message
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    member: Member = message.author

    prefix = appearance.get_prefix(guild.id)

    # Fetch invite or create new one
    server_invite: Invite = await channel.create_invite(reason='Server invite by fryselBot', unique=False)

    # Setup embed content
    embed: Embed = Embed()
    embed.title = 'Invite - ' + guild.name
    embed.description = server_invite.url

    # Setup embed style
    embed.colour = appearance.get_color(guild.id)
    embed.set_thumbnail(url=guild.icon_url)
    embed.set_footer(text=prefix + 'invite', icon_url=member.avatar_url)

    # Send embed & delete message
    await channel.send(embed=embed)
    await message.delete()
