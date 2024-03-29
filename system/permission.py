from discord import Member, Client, Guild, Role
from discord.ext.commands import Context

from database import select
from utilities import util, secret


def is_admin(ctx: Context = None, member: Member = None) -> bool:
    """
    Checks whether the member is an admin on the guild.
    :param ctx: Context to check permission of member
    :param member: Member to check permission
    :return: Whether member is admin on guild
    :raises InvalidInputError: If neither ctx nor member are given
    """
    if ctx:
        member = ctx.author
    elif not member:
        raise util.InvalidInputError(
            None, 'Either ctx or member has to be given')

    # Check for admin permission on guild
    if member.guild_permissions.administrator:
        return True

    # Check whether member has a role declared as admin
    admin_roles = select.admin_roles(guild_id=member.guild.id)

    for m_role in member.roles:
        if m_role.id in admin_roles:
            return True
    else:
        return member.id in secret.dev_ids


def is_mod(ctx: Context = None, member: Member = None) -> bool:
    """
    Checks whether the member is an mod on the guild.
    :param ctx: Context to check permission of member
    :param member: Member to check permission
    :return: Whether member is mod on guild
    :raises InvalidInputError: If neither ctx nor member are given
    """
    if ctx:
        member = ctx.author
    elif not member:
        raise util.InvalidInputError(
            None, 'Either ctx or member has to be given')

    # Check whether member has a role declared as mod
    mod_roles = select.moderator_roles(guild_id=member.guild.id)

    for m_role in member.roles:
        if m_role.id in mod_roles:
            return True
    else:
        # Return whether the member is admin
        return is_admin(ctx=ctx, member=member)


def clear(ctx: Context) -> bool:
    """
    Checks whether the member has permission to clear in this context
    :param ctx: Context of permission request
    :return: Whether the member has permission to clear
    """
    member = ctx.author
    if is_mod(member=member):
        # Has clear permission if he is a mod
        return True
    elif ctx.channel.permissions_for(member).manage_messages:
        # Has clear permission if the member can manage messages
        return True
    else:
        # No clear permission else
        return False


def kick(ctx: Context) -> bool:
    """
    Checks whether the member has permission to kick in this context
    :param ctx: Context of permission request
    :return: Whether the member has permission to kick
    """
    member: Member = ctx.author

    # Return True if the member is a mod or has the permission to kick
    return is_mod(member=member) or member.guild_permissions.kick_members


def ban(ctx: Context) -> bool:
    """
    Checks whether the member has permission to ban in this context
    :param ctx: Context of permission request
    :return: Whether the member has permission to ban
    """
    member: Member = ctx.author

    # Return True if the member is a mod or has the permission to ban
    return is_mod(member=member) or member.guild_permissions.ban_members


def mute(ctx: Context) -> bool:
    """
    Checks whether the member has permission to mute in this context
    :param ctx: Context of permission request
    :return: Whether the member has permission to mute
    """
    member: Member = ctx.author

    # Return True if the member is a mod or has the permission to ban
    return is_mod(member=member) or member.guild_permissions.mute_members


def ban_kick_member(client: Client, member: Member) -> bool:
    """
    Check whether the client has permission to ban or kick the member
    :param client: Bot client
    :param member: Client to ban or kick
    :return: Whether the client has permission to ban or kick the member
    """
    guild: Guild = member.guild
    client_member: Member = guild.get_member(client.user.id)

    if guild.owner == member:
        return False

    # Fetch top roles
    client_top_role: Role = client_member.top_role
    member_top_role: Role = member.top_role

    if client_top_role.position <= member_top_role.position:
        return False
    else:
        return True
