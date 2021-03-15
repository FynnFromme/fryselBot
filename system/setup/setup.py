from discord import Member, Embed, TextChannel, Guild, Message
from fryselBot.system import appearance, roles, welcome as welcome_sys, permission
from fryselBot.utilities import secret
from fryselBot.system.setup import prefix, color, welcome, roles, moderation, private_rooms


async def check_reactions(member: Member, guild: Guild, channel: TextChannel, message: Message, emoji: str,
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

    if member.id == secret.bot_id:
        # Ignore reactions from our bot
        return

    # Remove Reaction
    await message.remove_reaction(emoji, member)

    if member.bot:
        # Ignore reactions from bots
        return

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
                await color.color_page(channel, guild)
            elif emoji == '❗':
                # Call prefix page
                await prefix.prefix_page(channel, guild)
            elif emoji == '👥':
                # Call roles page
                await roles.roles_page(channel, guild)
            elif emoji == '👋':
                # Call welcome page
                await welcome.welcome_page(channel, guild)
            elif emoji == '👮🏽‍♂️':
                # Call moderation page
                await moderation.moderation_page(channel, guild)
            elif emoji == '🔉':
                # Call private rooms page
                await private_rooms.private_rooms_page(channel, guild)

        elif title == f'{bot_name} Setup - Prefix':
            if emoji == '❗':
                # Set prefix to default
                await prefix.setup_prefix(channel, guild)

        elif title == f'{bot_name} Setup - Color':
            if emoji == '🟧':
                # Set color to default
                await color.setup_color(channel, guild)

        elif title == f'{bot_name} Setup - Welcome':
            if emoji == '👋':
                # Toggle the welcome messages
                await welcome.toggle_welcome_messages(channel, guild, message)
            elif emoji == '📩':
                # Toggle the welcome DMs
                await welcome.toggle_welcome_dms(channel, guild, message)
            elif emoji == '🚶‍♂️':
                # Toggle the leave messages
                await welcome.toggle_leave_messages(channel, guild, message)
            elif emoji == '📄':
                # Send the welcome DM text
                await welcome_sys.welcome_dm(member, channel=channel, force=True)
        elif title == f'{bot_name} Setup - Moderation':
            if emoji == '📪':
                # Deactivate moderation log
                await moderation.setup_moderation_log(channel, guild, message)
            elif emoji == '👥':
                # Call roles page
                await roles.roles_page(channel, guild)
        elif title == f'{bot_name} Setup - Private Rooms':
            if emoji == '🔉':
                await private_rooms.toggle_private_rooms(channel, guild, message)


async def setup_page(channel: TextChannel, guild: Guild) -> None:
    """
    Sends a page with all information about the setup of the bot.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    """
    # Initialize important values
    guild_prefix = appearance.get_prefix(guild.id)

    # Setup appearance of the embed
    embed: Embed = Embed(title=f'{appearance.bot_name} - Setup',
                         description='Use the following commands or react.')
    embed.colour = appearance.get_color(guild.id)

    # Setup the command descriptions
    embed.add_field(name='Prefix ❗', value=f'`{guild_prefix}setup prefix`', inline=True)
    embed.add_field(name='Color  🟧', value=f'`{guild_prefix}setup color`', inline=True)
    embed.add_field(name='Roles  👥', value=f'`{guild_prefix}setup roles`', inline=True)
    embed.add_field(name='Welcome  👋', value=f'`{guild_prefix}setup welcome`', inline=True)
    embed.add_field(name='Moderation  👮🏽‍♂️', value=f'`{guild_prefix}setup moderation`', inline=True)
    embed.add_field(name='Private Rooms  🔉', value=f'`{guild_prefix}setup private rooms`', inline=True)

    # Send embed and add reactions
    message = await channel.send(embed=embed)
    await message.add_reaction(emoji='❗')
    await message.add_reaction(emoji='🟧')
    await message.add_reaction(emoji='👥')
    await message.add_reaction(emoji='👋')
    await message.add_reaction(emoji='👮🏽‍♂️')
    await message.add_reaction(emoji='🔉')
