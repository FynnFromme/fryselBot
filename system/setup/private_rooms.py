from discord import TextChannel, Guild, Embed, Message

from fryselBot.database import select
from fryselBot.system import appearance, description
from fryselBot.system.private_rooms import private_rooms


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
    is_set_up = select.cpr_channel_id(guild.id) is not None
    emoji = '✅' if is_set_up else '❌'

    # Setup the fields
    embed.add_field(name='Private Rooms Set Up?', value=emoji, inline=True)

    embed.add_field(name='Toggle Private Rooms', value='React with 🔉', inline=True)

    # embed.add_field(name='\u200b', value='\u200b', inline=True)

    # embed.add_field(name='Settings', value='\u200b', inline=True)

    # Send embed and add reactions
    message = await channel.send(embed=embed)

    await message.add_reaction(emoji='🔉')


async def toggle_private_rooms(channel: TextChannel, guild: Guild, setup_message: Message) -> None:
    """
    Toggles private rooms
    :param channel: Channel of the call
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
        await setup_message.edit(embed=embed)
    else:
        embed.set_field_at(0, name=embed_name, value='❌', inline=True)
        await setup_message.edit(embed=embed)
