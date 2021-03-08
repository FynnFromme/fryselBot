from discord import Member, Embed, TextChannel, Guild, Message, Role
from fryselBot.system import appearance, description, welcome, roles
from fryselBot.utilities import util, permission, secret
from fryselBot.database import select


async def reactions(member: Member, guild: Guild, channel: TextChannel, message: Message, emoji: str,
                    added: bool = True) -> None:
    """
    Handles the reactions added on setup messages.
    :param member: Member of reaction
    :param guild: Guild of reaction
    :param channel: Channel of reaction
    :param message: Message of reaction
    :param emoji: Emoji that was reacted
    :param added: Whether the reaction was added or removed
    """
    if message.author.id != secret.bot_id:
        # Ignore reactions on messages, that are from other ones
        return

    if member.bot:
        # Ignore reactions from bots
        return

    # Remove Reaction
    await message.remove_reaction(emoji, member)

    if not permission.is_admin(member=member):
        # Ignore reactions from members without admin permission
        return

    # Get the title of the message
    embeds = message.embeds
    if embeds:
        title = embeds[0].title
    else:
        # Return if the message isn't an embed
        return

    bot_name = appearance.bot_name

    # Reactions added
    if added:
        # Check for the different reactions
        if title == f'{bot_name} - Setup':
            if emoji == '🟧':
                # Call color page
                await color_page(channel, guild)
            elif emoji == '❗':
                # Call prefix page
                await prefix_page(channel, guild)
            elif emoji == '👋':
                # Call welcome page
                await welcome_page(channel, guild)
            elif emoji == '👥':
                # Call roles page
                await roles_page(channel, guild)

        elif title == f'{bot_name} Setup - Prefix':
            if emoji == '❗':
                # Set prefix to default
                await setup_prefix(channel, guild)

        elif title == f'{bot_name} Setup - Color':
            if emoji == '🟧':
                # Set color to default
                await setup_color(channel, guild)

        elif title == f'{bot_name} Setup - Welcome':
            if emoji == '👋':
                # Toggle the welcome messages
                await toggle_welcome_messages(channel, guild, message)
            elif emoji == '📩':
                # Toggle the welcome DMs
                await toggle_welcome_dms(channel, guild, message)
            elif emoji == '🚶‍♂️':
                # Toggle the leave messages
                await toggle_leave_messages(channel, guild, message)
            elif emoji == '📄':
                # Send the welcome DM text
                await welcome.welcome_dm(member, force=True)


async def setup_page(channel: TextChannel, guild: Guild) -> None:
    """
    Sends a page with all information about the setup of the bot.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    """
    # Initialize important values
    prefix = appearance.get_prefix(guild.id)

    # Setup appearance of the embed
    embed: Embed = Embed(title=f'{appearance.bot_name} - Setup',
                         description='Use the following commands or react.')
    embed.colour = appearance.get_color(guild.id)

    # Setup the command descriptions
    embed.add_field(name='Prefix ❗', value=f'`{prefix}setup prefix`', inline=True)
    embed.add_field(name='Color  🟧', value=f'`{prefix}setup color`', inline=True)
    embed.add_field(name='Roles  👥', value=f'`{prefix}setup roles`', inline=True)
    embed.add_field(name='Welcome  👋', value=f'`{prefix}setup welcome`', inline=True)
    embed.add_field(name='Coming Soon  ❓', value=f'`{prefix}setup ...`', inline=True)
    embed.add_field(name='Coming Soon  ❓', value=f'`{prefix}setup ... `', inline=True)

    # Send embed and add reactions
    message = await channel.send(embed=embed)
    await message.add_reaction(emoji='❗')
    await message.add_reaction(emoji='🟧')
    await message.add_reaction(emoji='👥')
    await message.add_reaction(emoji='👋')


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
    embed.add_field(name='Current prefix:', value=f'`{prefix}`', inline=False)
    embed.add_field(name='Set prefix:', value=f'`{prefix}{description.get_command("prefix").syntax}`', inline=False)

    embed.add_field(name='Valid prefix:', value='A single character.', inline=False)
    embed.add_field(name='Set to default:', value='React with ❗️', inline=False)

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

    # Setup the fields
    embed.add_field(name='Current color:', value=f'`{hex(appearance.get_color(guild.id))}`', inline=False)
    embed.add_field(name='Set color:', value=f'`{prefix}{description.get_command("color").syntax}`', inline=False)

    embed.add_field(name='Valid color:', value='HEX color code.', inline=False)
    embed.add_field(name='Set to default:', value='React with 🟧️', inline=False)

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
            raise util.InvalidInputError(color, "color has to be an hex-code or integer")
    else:
        # Set color to default
        appearance.set_color(guild.id)

    # Send response to command
    await channel.send(embed=Embed(description="The **color** was updated",
                                   colour=appearance.get_color(guild.id)))


async def welcome_page(channel: TextChannel, guild: Guild):
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
    embed.add_field(name='Welcome messages set up?', value=welcome_emoji, inline=True)
    embed.add_field(name='Toggle welcome messages:', value='React with 👋', inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=False)

    embed.add_field(name='Leave message set up?', value=leave_emoji, inline=True)
    embed.add_field(name='Toggle leave messages:', value='React with 🚶‍♂️', inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=False)

    embed.add_field(name='Welcome DMs setup?', value=welcome_dm_emoji, inline=True)
    embed.add_field(name='Toggle welcome DMs:', value='React with 📩', inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=False)

    if welcome_channel:
        embed.add_field(name='Welcome channel:', value=welcome_channel.mention, inline=True)

    embed.add_field(name='Set welcome channel:', value=f'`{prefix}{description.get_command("welcome channel").syntax}`',
                    inline=False)

    embed.add_field(name='\u200b', value='\u200b', inline=False)

    if welcome_dm:
        embed.add_field(name='Preview welcome DM:', value='React with 📄', inline=False)

    embed.add_field(name='Set welcome DM text:', value=f'`{prefix}{description.get_command("welcome dm").syntax}`'
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


async def setup_welcome_channel(channel: TextChannel, guild: Guild, message: Message, welcome_channel: TextChannel):
    """
    Sets up the welcome channel for the server.
    :param channel: Channel of message
    :param guild: Guild of welcome channel
    :param message: Message of the command call
    :param welcome_channel: The channel, welcome channel will be set to
    """
    # Delete message of member
    await util.delete_message(message)

    welcome.set_welcome_channel(guild, welcome_channel.id)

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
                                   colour=appearance.red_color)
        error_message = await channel.send(embed=error_embed)
        await error_message.delete(delay=10)
    else:
        # Toggle the welcome messages
        welcome.toggle_welcome(guild)
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
                                   colour=appearance.red_color)
        error_message = await channel.send(embed=error_embed)
        await error_message.delete(delay=10)
    else:
        # Toggle the leave messages
        welcome.toggle_leave(guild)
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
                                   colour=appearance.red_color)
        error_message = await channel.send(embed=error_embed)
        await error_message.delete(delay=10)
    else:
        # Toggle the welcome dms
        welcome.toggle_welcome_dm(guild)
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

    welcome.set_welcome_dm(guild, text)

    # Send response to command
    await channel.send(embed=Embed(description=f"The text for **welcome DMs** was set to:\n*'{text}'*",
                                   colour=appearance.get_color(guild.id)))


async def roles_page(channel: TextChannel, guild: Guild) -> None:
    """
    Sends a page with all information about the setup of roles.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    """
    # Initialize important values
    prefix = appearance.get_prefix(guild.id)

    # Setup appearance of the embed
    embed: Embed = Embed(title=f'{appearance.bot_name} Setup - Roles',
                         description='Setup the roles!',
                         colour=appearance.get_color(guild.id))

    # Get existing roles
    admin_roles = '\n'.join(map(lambda r: r.mention, roles.get_admin_roles(guild)))
    moderator_roles = '\n'.join(map(lambda r: r.mention, roles.get_moderator_roles(guild)))
    support_roles = '\n'.join(map(lambda r: r.mention, roles.get_support_roles(guild)))

    # Add information about the roles already existing to embed
    if admin_roles:
        embed.add_field(name='Admin Roles', value=admin_roles, inline=False)
    if moderator_roles:
        embed.add_field(name='Moderator Roles', value=moderator_roles, inline=False)
    if support_roles:
        embed.add_field(name='Support Roles', value=support_roles, inline=False)

    # Add information about the commands
    embed.add_field(name='Add Roles', value=f'`{prefix}{description.get_command("roles add").syntax}`'
                                            f'\nThe type is either *admin*, *moderator* or *supporter* .',
                    inline=False)
    embed.add_field(name='Remove Roles', value=f'`{prefix}{description.get_command("roles remove").syntax}`'
                                               f'\nThe type is either *admin*, *moderator* or *supporter*.',
                    inline=False)

    await channel.send(embed=embed)


async def add_role(guild: Guild, role: Role, type_: str, channel: TextChannel, message: Message) -> None:
    """
    Add a role of the server
    :param guild: Guild of the role
    :param role: Role
    :param type_: Type of the role
    :param channel: Channel of message
    :param message: Message of the command call
    """
    # Delete message of member
    await util.delete_message(message)

    # Check for type and add the role
    type_ = type_.lower()
    if type_ == 'admin':
        roles.add_admin_role(guild, role)
    elif type_ == 'moderator':
        roles.add_moderator_role(guild, role)
    elif type_ == 'supporter':
        roles.add_support_role(guild, role)
    else:
        raise Exception('Invalid type')

    # Send message
    embed: Embed = Embed(description=f'Added {role.mention} to **{type_} roles**',
                         colour=appearance.get_color(guild.id))
    await channel.send(embed=embed)


async def remove_role(guild: Guild, role: Role, type_: str, channel: TextChannel, message: Message) -> None:
    """
    Remove a role from the server
    :param guild: Guild of the role
    :param role: Role
    :param type_: Type of the role
    :param channel: Channel of message
    :param message: Message of the command call
    """
    # Dele
    # Delete message of member
    await util.delete_message(message)

    # Check for type and remove the role
    type_ = type_.lower()
    if type_ == 'admin':
        roles.remove_admin_role(role)
    elif type_ == 'moderator':
        roles.remove_moderator_role(role)
    elif type_ == 'supporter':
        roles.remove_support_role(role)
    else:
        raise Exception('Invalid type')

    # Send message
    embed: Embed = Embed(description=f'Removed {role.mention} from **{type_} roles**',
                         colour=appearance.get_color(guild.id))
    await channel.send(embed=embed)
