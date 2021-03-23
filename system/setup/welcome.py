from discord import TextChannel, Guild, Embed, Message

from database import select
from system import appearance, description, welcome as welcome_sys
from utilities import util


async def welcome_page(channel: TextChannel, guild: Guild) -> None:
    """
    Sends a page with all information about the setup of the welcome system.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    """

    # Initialize important values
    prefix = appearance.get_prefix(guild.id)

    # Setup appearance of the embed
    embed: Embed = Embed(title=f'{appearance.bot_name} Setup - Welcome',
                         description='Setup the welcome system!')
    embed.colour = appearance.get_color(guild.id)

    # Emojis whether welcome/leave is setup
    welcome_dm_emoji = '✅' if select.welcome_dms(guild.id) else '❌'
    welcome_emoji = '✅' if select.welcome_messages(guild.id) else '❌'
    leave_emoji = '✅' if select.leave_messages(guild.id) else '❌'

    welcome_channel: TextChannel = guild.get_channel(select.welcome_channel_id(guild.id))
    welcome_dm = select.welcome_dm(guild.id)

    # Setup the fields
    embed.add_field(name='Welcome Messages Set Up?', value=welcome_emoji, inline=True)
    embed.add_field(name='Toggle Welcome Messages', value='React with 👋', inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=True)

    embed.add_field(name='Leave Message Set Up?', value=leave_emoji, inline=True)
    embed.add_field(name='Toggle Leave Messages', value='React with 🚶‍♂️', inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=True)

    embed.add_field(name='Welcome DMs Set Up?', value=welcome_dm_emoji, inline=True)
    embed.add_field(name='Toggle Welcome DMs', value='React with 📩', inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=False)

    if welcome_channel:
        embed.add_field(name='Welcome Channel', value=welcome_channel.mention, inline=True)

    embed.add_field(name='Set Welcome Channel', value=f'`{prefix}{description.get_command("welcome channel").syntax}`',
                    inline=False)

    embed.add_field(name='\u200b', value='\u200b', inline=False)

    if welcome_dm:
        embed.add_field(name='Preview Welcome DM', value='React with 📄', inline=False)

    embed.add_field(name='Set Welcome DM Text', value=f'`{prefix}{description.get_command("welcome dm").syntax}`'
                                                      f"\n'<member>' will be replaced by the name"
                                                      f"\nof the member.",
                    inline=False)

    # Send embed and add reactions
    message = await channel.send(embed=embed)

    await message.add_reaction(emoji='👋')
    await message.add_reaction(emoji='🚶‍♂️')
    await message.add_reaction(emoji='📩')
    if welcome_dm:
        await message.add_reaction(emoji='📄')


async def setup_welcome_channel(channel: TextChannel, guild: Guild, message: Message,
                                welcome_channel: TextChannel) -> None:
    """
    Sets up the welcome channel for the server.
    :param channel: Channel of message
    :param guild: Guild of welcome channel
    :param message: Message of the command call
    :param welcome_channel: The channel, welcome channel will be set to
    """
    # Delete message of member
    await util.delete_message(message)

    welcome_sys.set_welcome_channel(guild, welcome_channel.id)

    # Send response to command
    await channel.send(embed=Embed(description=f"The **welcome channel** was set to {welcome_channel.mention}",
                                   colour=appearance.get_color(guild.id)))


async def toggle_welcome_messages(channel: TextChannel, guild: Guild, setup_message: Message) -> None:
    """
    Toggles welcome messages
    :param channel: Channel of the call
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    if not select.welcome_channel_id(guild.id) and not select.welcome_messages(guild.id):
        # The welcome_channel has to be set first before enabling welcome messages
        prefix = appearance.get_prefix(guild.id)
        # Send error message and delete it
        error_embed: Embed = Embed(title='Welcome channel has to be set',
                                   description=f'Set the welcome channel first using `{prefix}'
                                               f'{description.get_command("welcome channel").syntax}`',
                                   colour=appearance.error_color)
        error_message = await channel.send(embed=error_embed)
        await error_message.delete(delay=10)
    else:
        # Toggle the welcome messages
        welcome_sys.toggle_welcome(guild)
        new_status = select.welcome_messages(guild.id)

        # Change status within the embed
        embed = setup_message.embeds[0]
        embed_name = embed.fields[0].name
        if new_status:
            embed.set_field_at(0, name=embed_name, value='✅', inline=True)
            await setup_message.edit(embed=embed)
        else:
            embed.set_field_at(0, name=embed_name, value='❌', inline=True)
            await setup_message.edit(embed=embed)


async def toggle_leave_messages(channel: TextChannel, guild: Guild, setup_message: Message) -> None:
    """
    Toggles leave messages
    :param channel: Channel of the call
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    if not select.welcome_channel_id(guild.id) and not select.leave_messages(guild.id):
        # The welcome_channel has to be set first before enabling leave messages
        prefix = appearance.get_prefix(guild.id)
        # Send error message and delete it
        error_embed: Embed = Embed(title='Welcome channel has to be set',
                                   description=f'Set the welcome channel first using `{prefix}'
                                               f'{description.get_command("welcome channel").syntax}`',
                                   colour=appearance.error_color)
        error_message = await channel.send(embed=error_embed)
        await error_message.delete(delay=10)
    else:
        # Toggle the leave messages
        welcome_sys.toggle_leave(guild)
        new_status = select.leave_messages(guild.id)

        # Change status within the embed
        embed = setup_message.embeds[0]
        embed_name = embed.fields[3].name
        if new_status:
            embed.set_field_at(3, name=embed_name, value='✅', inline=True)
            await setup_message.edit(embed=embed)
        else:
            embed.set_field_at(3, name=embed_name, value='❌', inline=True)
            await setup_message.edit(embed=embed)


async def toggle_welcome_dms(channel: TextChannel, guild: Guild, setup_message: Message) -> None:
    """
    Toggles welcome dms
    :param channel: Channel of the call
    :param guild: Guild of the call
    :param setup_message: The message where the reaction was edited
    """
    if not select.welcome_dm(guild.id) and not select.welcome_dms(guild.id):
        # The welcome dm has to be set first before enabling welcome dms
        prefix = appearance.get_prefix(guild.id)
        # Send error message and delete it
        error_embed: Embed = Embed(title='Welcome DM text has to be set',
                                   description=f'Set the welcome DM text first using `{prefix}'
                                               f'{description.get_command("welcome dm").syntax}`',
                                   colour=appearance.error_color)
        error_message = await channel.send(embed=error_embed)
        await error_message.delete(delay=10)
    else:
        # Toggle the welcome dms
        welcome_sys.toggle_welcome_dm(guild)
        new_status = select.welcome_dms(guild.id)

        # Change status within the embed
        embed = setup_message.embeds[0]
        embed_name = embed.fields[6].name
        if new_status:
            embed.set_field_at(6, name=embed_name, value='✅', inline=True)
            await setup_message.edit(embed=embed)
        else:
            embed.set_field_at(6, name=embed_name, value='❌', inline=True)
            await setup_message.edit(embed=embed)


async def setup_welcome_dm_text(channel: TextChannel, guild: Guild, message: Message, text: str) -> None:
    """
    Sets up the welcome dm text for the server.
    :param channel: Channel of message
    :param guild: Guild of welcome channel
    :param message: Message of the command call
    :param text: The text for the welcome messages via dm
    """
    # Delete message of member
    await util.delete_message(message)

    welcome_sys.set_welcome_dm(guild, text)

    # Send response to command
    await channel.send(embed=Embed(description=f"The text for **welcome DMs** was set to:\n*'{text}'*",
                                   colour=appearance.get_color(guild.id)))
