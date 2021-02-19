from discord import Member
from discord.ext.commands import Context

from fryselBot.database import select
from fryselBot.utilities import util


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
        raise util.InvalidInputError(None, "Either ctx or member has to be given")

    # Check for admin permission on guild
    if member.guild_permissions.administrator:
        return True

    # Check whether member has a role declared as admin
    admin_roles = select.admin_roles(guild_id=member.guild.id)

    for m_role in member.roles:
        if m_role.id in admin_roles:
            return True
    else:
        return False


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
        raise util.InvalidInputError(None, "Either ctx or member has to be given")

    # Check whether member has a role declared as mod
    mod_roles = select.mod_roles(guild_id=member.guild.id)

    for m_role in member.roles:
        if m_role.id in mod_roles:
            return True
    else:
        return False
