from discord import TextChannel, Guild, Embed, Message, Member

from database import select, update
from database.select import PrivateRoom
from system import appearance
from system.private_rooms import private_rooms, settings as pr_settings, settings


async def private_rooms_page(channel: TextChannel, guild: Guild) -> None:
    """
    Sends a page with all information about the setup of private rooms
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    """

    # Initialize important values
    prefix = appearance.get_prefix(guild.id)

    # Setup appearance of the embed
    embed: Embed = Embed(title=f'{appearance.bot_name} Setup - Private Rooms',
                         description='Setup private rooms!')
    embed.colour = appearance.get_color(guild.id)

    # Emojis whether private rooms are setup
    set_up_emoji = '✅' if select.cpr_channel_id(guild.id) is not None else '❌'
    text_channel_emoji = '✅' if select.pr_text_channel_activated(guild.id) else '❌'
    name_emoji = '✅' if select.pr_change_name(guild.id) else '❌'
    privacy_emoji = '✅' if select.pr_change_privacy(guild.id) else '❌'
    limit_emoji = '✅' if select.pr_change_limit(guild.id) else '❌'
    visibility_emoji = '✅' if select.pr_change_visibility(guild.id) else '❌'

    # Setup the fields
    embed.add_field(name='Private Rooms Set Up?', value=set_up_emoji, inline=True)

    embed.add_field(name='Toggle Private Rooms', value='React with 🔉', inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=False)

    embed.add_field(name='Default Settings', value='React with ⚙️ to set your current private room settings to the '
                                                   'default ones of the server', inline=False)

    embed.add_field(name='\u200b', value='\u200b', inline=False)

    embed.add_field(name='Toggle Settings', value='React with the corresponding reaction to toggle whether the setting '
                                                  'can be used on your server', inline=False)

    embed.add_field(name='Text Channels #️⃣', value=text_channel_emoji, inline=True)

    embed.add_field(name='Name 🪧', value=name_emoji, inline=True)

    embed.add_field(name='Privacy 🔒', value=privacy_emoji, inline=True)

    embed.add_field(name='Limit 🔢', value=limit_emoji, inline=True)

    embed.add_field(name='Visibility 👀', value=visibility_emoji, inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=True)

    # Send embed and add reactions
    message = await channel.send(embed=embed)

    await message.add_reaction(emoji='🔉')
    await message.add_reaction(emoji='⚙️')
    await message.add_reaction(emoji='#️⃣')
    await message.add_reaction(emoji='🪧')
    await message.add_reaction(emoji='🔒')
    await message.add_reaction(emoji='🔢')
    await message.add_reaction(emoji='👀')


async def toggle_private_rooms(guild: Guild, setup_message: Message) -> None:
    """
    Toggles private rooms
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    is_set_up = select.cpr_channel_id(guild.id) is not None
    new_status = not is_set_up

    # Setup or disable the private rooms on guild
    if new_status:
        await private_rooms.setup_private_rooms(guild)
    else:
        await private_rooms.disable(guild)

    # Change status within the embed
    embed = setup_message.embeds[0]
    embed_name = embed.fields[0].name
    if new_status:
        embed.set_field_at(0, name=embed_name, value='✅', inline=True)
    else:
        embed.set_field_at(0, name=embed_name, value='❌', inline=True)

    await setup_message.edit(embed=embed)


async def toggle_text_channel(guild: Guild, setup_message: Message) -> None:
    """
    Toggles whether private rooms have text channels
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    new_status = not select.pr_text_channel_activated(guild.id)

    # Setup or disable the private rooms on guild
    update.pr_text_channel_activated(argument=guild.id, value=new_status)

    # Change status within the embed
    embed = setup_message.embeds[0]
    embed_name = embed.fields[7].name
    if new_status:
        embed.set_field_at(7, name=embed_name, value='✅', inline=True)
    else:
        embed.set_field_at(7, name=embed_name, value='❌', inline=True)

    await setup_message.edit(embed=embed)


async def toggle_name(guild: Guild, setup_message: Message) -> None:
    """
    Toggles whether private rooms can change the name
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    new_status = not select.pr_change_name(guild.id)

    # Setup or disable the private rooms on guild
    update.pr_change_name(argument=guild.id, value=new_status)

    # Change status within the embed
    embed = setup_message.embeds[0]
    embed_name = embed.fields[8].name
    if new_status:
        embed.set_field_at(8, name=embed_name, value='✅', inline=True)
    else:
        embed.set_field_at(8, name=embed_name, value='❌', inline=True)

    await setup_message.edit(embed=embed)

    await settings.setup_settings(guild)


async def toggle_privacy(guild: Guild, setup_message: Message) -> None:
    """
    Toggles whether private rooms can change privacy
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    new_status = not select.pr_change_privacy(guild.id)
    # Setup or disable the private rooms on guild
    update.pr_change_privacy(argument=guild.id, value=new_status)

    # Change status within the embed
    embed = setup_message.embeds[0]
    embed_name = embed.fields[9].name
    if new_status:
        embed.set_field_at(9, name=embed_name, value='✅', inline=True)
    else:
        embed.set_field_at(9, name=embed_name, value='❌', inline=True)

    await setup_message.edit(embed=embed)

    await settings.setup_settings(guild)


async def toggle_limit(guild: Guild, setup_message: Message) -> None:
    """
    Toggles whether private rooms can change the user limit
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    new_status = not select.pr_change_limit(guild.id)

    # Setup or disable the private rooms on guild
    update.pr_change_limit(argument=guild.id, value=new_status)

    # Change status within the embed
    embed = setup_message.embeds[0]
    embed_name = embed.fields[10].name
    if new_status:
        embed.set_field_at(10, name=embed_name, value='✅', inline=True)
    else:
        embed.set_field_at(10, name=embed_name, value='❌', inline=True)

    await setup_message.edit(embed=embed)

    await settings.setup_settings(guild)


async def toggle_visibility(guild: Guild, setup_message: Message) -> None:
    """
    Toggles whether private rooms can change visibility
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    new_status = not select.pr_change_visibility(guild.id)

    # Setup or disable the private rooms on guild
    update.pr_change_visibility(argument=guild.id, value=new_status)

    # Change status within the embed
    embed = setup_message.embeds[0]
    embed_name = embed.fields[11].name
    if new_status:
        embed.set_field_at(11, name=embed_name, value='✅', inline=True)
    else:
        embed.set_field_at(11, name=embed_name, value='❌', inline=True)

    await setup_message.edit(embed=embed)

    await settings.setup_settings(guild)


async def set_default_settings(member: Member, channel: TextChannel) -> None:
    """

    :param member:
    :param channel:
    """

    if not private_rooms.has_private_room(member):
        embed: Embed = Embed(description='You must be the owner of a private room to do that',
                             colour=appearance.error_color)
        error_msg = await channel.send(embed=embed)
        await error_msg.delete(delay=10)
        return

    guild: Guild = member.guild
    private_room: PrivateRoom = PrivateRoom(guild_id=guild.id, owner_id=member.id)

    pr_settings.set_default(guild, private_room)
    embed: Embed = Embed(title='Updated Default Private Room Settings', colour=appearance.get_color(guild.id))

    # Add information about game activity
    if private_room.game_activity:
        embed.add_field(name='Game Activity', value='Game activity will be shown 🎮', inline=False)
    else:
        embed.add_field(name='Game Activity', value='Game activity will not be shown', inline=False)

    # Add information about privacy status
    if private_room.locked:
        embed.add_field(name='Privacy', value='Private rooms will be locked 🔒', inline=False)
    else:
        embed.add_field(name='Privacy', value='Private rooms will be unlocked 🔓', inline=False)

    # Add information about limit
    if private_room.user_limit == 0:
        embed.add_field(name='Limit', value='No limit 🔄 by default', inline=False)
    else:
        embed.add_field(name='Limit', value=f'Default limit is set to `{private_room.user_limit}`', inline=False)

    # Add information about visibiltiy status
    if private_room.hidden:
        embed.add_field(name='Visibility', value='Rooms will be hidden by default 🚫', inline=False)
    else:
        embed.add_field(name='Visibility', value='Rooms will be visible by default 👀', inline=False)

    await channel.send(embed=embed)
