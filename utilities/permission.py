from discord import Member

from fryselBot.database import select


def is_admin(member: Member) -> bool:
    """
    Checks whether the member is an admin on the guild.
    :param member: Member to check permission
    :return: Whether member is admin on guild
    """
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


def is_mod(member: Member) -> bool:
    """
    Checks whether the member is an mod on the guild.
    :param member: Member to check permission
    :return: Whether member is mod on guild
    """

    # Check whether member has a role declared as mod
    mod_roles = select.mod_roles(guild_id=member.guild.id)

    for m_role in member.roles:
        if m_role.id in mod_roles:
            return True
    else:
        return False
