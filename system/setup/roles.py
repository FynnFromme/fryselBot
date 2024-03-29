from discord import TextChannel, Guild, Embed, Role, Message

from system import appearance, roles, description
from utilities import util


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
    # support_roles = '\n'.join(map(lambda r: r.mention, roles.get_support_roles(guild)))
    auto_roles = '\n'.join(map(lambda r: r.mention, roles.get_auto_roles(guild)))

    # Add information about the roles already existing to embed
    if admin_roles:
        embed.add_field(name='Admin Roles', value=admin_roles, inline=True)
    if moderator_roles:
        embed.add_field(name='Moderator Roles', value=moderator_roles, inline=True)
    # if support_roles:
    #     embed.add_field(name='Support Roles', value=support_roles, inline=True)
    if auto_roles:
        embed.add_field(name='Autoroles', value=auto_roles, inline=True)

    embed.add_field(name='\u200b', value='\u200b', inline=False)

    # Add information about the commands
    embed.add_field(name='Add Roles', value=f'`{prefix}{description.get_command("roles add").syntax}`'
                                            f'\nThe type is either *admin*, *moderator* or *autorole*.',
                    inline=False)
    embed.add_field(name='Remove Roles', value=f'`{prefix}{description.get_command("roles remove").syntax}`'
                                               f'\nThe type is either *admin*, *moderator* or *autorole*.',
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
    # elif type_ == 'supporter':
    #     roles.add_support_role(guild, role)
    elif type_ == 'autorole':
        roles.add_auto_role(guild, role)
    else:
        raise Exception('Invalid type')

    # Send message
    if type_ == 'autorole':
        embed: Embed = Embed(description=f'Added {role.mention} to **{type_}s**',
                             colour=appearance.get_color(guild.id))
    else:
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
    # elif type_ == 'supporter':
    #     roles.remove_support_role(role)
    elif type_ == 'autorole':
        roles.remove_auto_role(role)
    else:
        raise Exception('Invalid type')

    # Send message
    if type_ == 'autorole':
        embed: Embed = Embed(description=f'Removed {role.mention} from **{type_}s**',
                             colour=appearance.get_color(guild.id))
    else:
        embed: Embed = Embed(description=f'Removed {role.mention} from **{type_} roles**',
                             colour=appearance.get_color(guild.id))
    await channel.send(embed=embed)
