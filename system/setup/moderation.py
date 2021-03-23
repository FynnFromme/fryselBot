from discord import TextChannel, Guild, Embed, Role, Message

from system import appearance, description
from system.moderation import moderation as mod, mute
from utilities import util


async def moderation_page(channel: TextChannel, guild: Guild):
    """
    Sends a page with all information about the setup of moderation.
    :param guild: Guild of call
    :param channel: TextChannel to send the message to
    """
    # Initialize important values
    prefix = appearance.get_prefix(guild.id)

    # Setup appearance of the embed
    embed: Embed = Embed(title=f'{appearance.bot_name} Setup - Moderation',
                         description='Setup the moderation system!',
                         colour=appearance.get_color(guild.id))

    # Add information about moderation roles
    embed.add_field(name='Set Moderation Roles', value=f'React with 👥', inline=False)

    mod_log: TextChannel = mod.get_mod_log(guild)
    # Add information about the current moderation log
    embed.add_field(name='\u200b', value='\u200b', inline=False)

    embed.add_field(name='Moderation Log', value='• Get notified of mod operations\n'
                                                 '• Unlock reports',
                    inline=False)
    if mod_log:
        embed.add_field(name='Current Channel', value=mod_log.mention, inline=False)

    # Add information about the commands
    embed.add_field(name='Set Moderation Log', value=f'`{prefix}{description.get_command("moderation log").syntax}`',
                    inline=False)

    # How to deactivate moderation log
    if mod_log:
        embed.add_field(name='Deactivate Moderation Log', value='React with 📪', inline=False)

    # Add information about the warn system
    embed.add_field(name='\u200b', value='\u200b', inline=False)
    embed.add_field(name='Warn Punishment', value=f'• **1 warn:**  20 min mute\n'
                                                  f'• **3 warns within two weeks:**  2h mute\n'
                                                  f'• **4 warns within one month:**  24h mute & kick')

    # Add information about mute
    mute_role: Role = await mute.get_mute_role(guild)
    embed.add_field(name='\u200b', value='\u200b', inline=False)
    embed.add_field(name='Problems With Mute?', value=f'Make sure the position of {mute_role.mention} is high enough.')

    # Send embed
    msg = await channel.send(embed=embed)

    # Add reactions
    await msg.add_reaction('👥')
    if mod_log:
        await msg.add_reaction('📪')


async def setup_moderation_log(channel: TextChannel, guild: Guild, message: Message,
                               mod_log: TextChannel = None) -> None:
    """
    Set up th moderation log channel for the server
    :param channel: Channel of message
    :param guild: Guild for moderation log
    :param message: Message of the command call
    :param mod_log: The channel set as moderation log
    """
    if mod_log:
        # Delete message of member
        await util.delete_message(message)

        # Throw exception if the mod_log isn't a channel of the guild
        if mod_log not in guild.channels:
            raise util.InvalidInputError(mod_log, 'The moderation log has to be a text-channel of the server.')

        # Set moderation log
        mod.set_mod_log(guild, mod_log.id)

        # Send response to command
        await channel.send(embed=Embed(description=f'The **moderation log** was set to {mod_log.mention}',
                                       colour=appearance.get_color(guild.id)))
    else:
        # Deactivate moderation log
        mod.set_mod_log(guild, None)

        # Send response to command
        await channel.send(embed=Embed(description='The **moderation log** was deactivated',
                                       colour=appearance.get_color(guild.id)))
