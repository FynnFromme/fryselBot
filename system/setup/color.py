from discord import TextChannel, Guild, Embed, Message

from system import appearance, description
from utilities import util


async def color_page(channel: TextChannel, guild: Guild) -> None:
    """
    Sends a page with all information about the setup of the color.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    """
    # Initialize important values
    prefix = appearance.get_prefix(guild.id)

    # Setup appearance of the embed
    embed: Embed = Embed(title=f'{appearance.bot_name} Setup - Color',
                         description='Setup your custom color!')
    embed.colour = appearance.get_color(guild.id)

    # Fetch colorand format to hex color code
    color = hex(appearance.get_color(guild.id))
    color = '#' + str(color)[2:]

    # Setup the fields
    embed.add_field(name='Current Color', value=f'`{color}`', inline=False)
    embed.add_field(
        name='Set Color', value=f'`{prefix}{description.get_command("color").syntax}`', inline=False)

    embed.add_field(name='Valid Color', value='HEX color code', inline=False)
    embed.add_field(name='Set To Default', value='React with 🟧️', inline=False)

    # Send embed and add reactions
    message = await channel.send(embed=embed)
    await message.add_reaction(emoji='🟧')


async def setup_color(channel: TextChannel, guild: Guild, message: Message = None, color: str = None) -> None:
    """
    Command for setting prefix on guild.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    :param message: Message that called the command
    :param color: The given primary color hex-code
    :raises InvalidInputError: When the given primary_color isn't 'default', hex-color code or integer
    """
    # Delete message of member
    await util.delete_message(message)

    # Set color to valid integer
    if color:
        try:
            if color.startswith("#"):
                color = int("0x" + color[1:], 16)

            elif color.startswith("0x"):
                color = int(color, 16)

            else:
                color = int("0x" + color, 16)

            # Set primary color of the server
            appearance.set_color(guild_id=guild.id, color=color)
        except TypeError:
            raise util.InvalidInputError(
                color, "color has to be an hex-code or integer")
    else:
        # Set color to default
        appearance.set_color(guild.id)

    # Send response to command
    await channel.send(embed=Embed(description="The **color** was updated",
                                   colour=appearance.get_color(guild.id)))
