from discord import Guild, Role
from fryselBot.database import select, insert, delete


def add_admin_role(guild: Guild, role: Role) -> None:
    """
    Add admin role to database.
    :param guild: Guild to add the role
    :param role: Role that will be added
    """
    # Throw exception if the role isn't a role of the guild
    if role not in guild.roles:
        raise Exception('role has to be a role on the guild')

    # Ignore if the role is already marked as an admin role
    if role.id in select.admin_roles(guild.id):
        return

    # Insert role to database
    insert.role(role.id, 'ADMIN', guild.id)


def remove_admin_role(role: Role) -> None:
    """
    Remove admin role from database.
    :param role: Role that will be removed
    """
    # Delete role from database
    delete.role(role.id, type='ADMIN')


def get_admin_roles(guild: Guild) -> list:
    """
    Creates a list of all admin roles on the guild
    :param guild: Guild to search admin roles
    :return: List of all admin roles on the guild
    """
    # Get all IDs of admin roles
    role_ids = select.admin_roles(guild.id)

    # Create list of all roles
    roles = []
    for role_id in role_ids:
        roles.append(guild.get_role(role_id))

    return roles


def add_moderator_role(guild: Guild, role: Role) -> None:
    """
    Add moderator role to database.
    :param guild: Guild to add the role
    :param role: Role that will be added
    """
    # Throw exception if the role isn't a role of the guild
    if role not in guild.roles:
        raise Exception('role has to be a role on the guild')

    # Ignore if the role is already marked as a moderator role
    if role.id in select.moderator_roles(guild.id):
        return

    # Insert role to database
    insert.role(role.id, 'MODERATOR', guild.id)


def remove_moderator_role(role: Role) -> None:
    """
    Remove moderator role from database.
    :param role: Role that will be removed
    """
    # Delete role from database
    delete.role(role.id, type='MODERATOR')


def get_moderator_roles(guild: Guild) -> list:
    """
    Creates a list of all moderator roles on the guild
    :param guild: Guild to search moderator roles
    :return: List of all moderator roles on the guild
    """
    # Get all IDs of moderator roles
    role_ids = select.moderator_roles(guild.id)

    # Create list of all roles
    roles = []
    for role_id in role_ids:
        roles.append(guild.get_role(role_id))

    return roles


def add_support_role(guild: Guild, role: Role) -> None:
    """
    Add support role to database.
    :param guild: Guild to add the role
    :param role: Role that will be added
    """
    # Throw exception if the role isn't a role of the guild
    if role not in guild.roles:
        raise Exception('role has to be a role on the guild')

    # Ignore if the role is already marked as a support role
    if role.id in select.support_roles(guild.id):
        return

    # Insert role to database
    insert.role(role.id, 'SUPPORTER', guild.id)


def remove_support_role(role: Role) -> None:
    """
    Remove support role from database.
    :param role: Role that will be removed
    """
    # Delete role from database
    delete.role(role.id, type='SUPPORTER')


def get_support_roles(guild: Guild) -> list:
    """
    Creates a list of all support roles on the guild
    :param guild: Guild to search support roles
    :return: List of all support roles on the guild
    """
    # Get all IDs of support roles
    role_ids = select.support_roles(guild.id)

    # Create list of all roles
    roles = []
    for role_id in role_ids:
        roles.append(guild.get_role(role_id))

    return roles
