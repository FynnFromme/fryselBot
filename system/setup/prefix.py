from discord import TextChannel, Guild, Embed, Message
from fryselBot.system import appearance, description
from fryselBot.utilities import util


async def prefix_page(channel: TextChannel, guild: Guild) -> None:
    """
    Sends a page with all information about the setup of the prefix.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    """
    # Initialize important values
    prefix = appearance.get_prefix(guild.id)

    # Setup appearance of the embed
    embed: Embed = Embed(title=f'{appearance.bot_name} Setup - Prefix',
                         description='Setup your custom prefix!')
    embed.colour = appearance.get_color(guild.id)

    # Setup the fields
    embed.add_field(name='Current Prefix', value=f'`{prefix}`', inline=False)
    embed.add_field(name='Set Prefix', value=f'`{prefix}{description.get_command("prefix").syntax}`', inline=False)

    embed.add_field(name='Valid Prefix', value='A single character.', inline=False)
    embed.add_field(name='Set To Default', value='React with ❗️', inline=False)

    # Send embed and add reactions
    message = await channel.send(embed=embed)
    await message.add_reaction(emoji='❗')


async def setup_prefix(channel: TextChannel, guild: Guild, message: Message = None, prefix: str = None) -> None:
    """
    Command for setting prefix on guild.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    :param message: Message that called the command
    :param prefix: The given prefix
    :raises InvalidInputError: When the given prefix isn't 'default' or a single character
    """
    # Delete message of member
    await util.delete_message(message)

    appearance.set_prefix(guild_id=guild.id, prefix=prefix)

    # Send response to command
    await channel.send(embed=Embed(description=f"The **prefix** was set to `{appearance.get_prefix(guild.id)}`",
                                   colour=appearance.get_color(guild.id)))
