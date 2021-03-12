from fryselBot.database._manager import connection, DatabaseAttributeError, DatabaseError
from sqlite3.dbapi2 import Cursor
from fryselBot.utilities import util

import datetime


@connection
def generate_new_id(_c: Cursor, table: str, identifier: str) -> str:
    """
    Generate a unique ID in table for identifier
    :param _c: Cursor (provided by decorator)
    :param table: Database table
    :param identifier: Identifier of id attribute
    :return: Unique ID
    """
    unique = False
    count = 0
    random_id = None
    # Create new IDs until the id is unique
    while not unique:
        # Generate new ID
        random_id = util.random_base_16_code()

        # Get entries that have the same ID
        _c.execute("SELECT * FROM {} WHERE {}=='{}' LIMIT 1".format(table, identifier, random_id))
        result = _c.fetchone()

        # Check whether the ID is already used
        if not result:
            unique = True

        # No infinite loop
        count += 1
        if count >= 1000000:
            raise DatabaseError('No unique code could be generated for table: {}'.format(table))

    return random_id


@connection
def guild(_c: Cursor, guild_id: int, welcome_channel_id: int = None, cpr_channel_id: int = None,
          pr_settings_id: int = None,
          mod_log_id: int = None,
          support_log_id: int = None,
          ticket_category_id: int = None,
          mute_role_id: int = None) -> None:
    """
    Insert guild into db.
    :param _c: Database cursor (provided by decorator)
    :param guild_id: Discord GuildID
    :param welcome_channel_id: Discord TextChannelID
    :param cpr_channel_id: Discord VoiceChannelID (cpr: create private room)
    :param pr_settings_id: Discord TextChannelID (pr: private room)
    :param mod_log_id: Discord TextChannelID
    :param support_log_id: Discord TextChannelID
    :param ticket_category_id: Discord CategoryID
    :param mute_role_id: ID of Mute role
    """
    # Insert into db
    _c.execute('''INSERT INTO guilds VALUES (:guild_id, :welcome_channel_id, :cpr_channel_id, :pr_settings_id, 
                :mod_log_id, :support_log_id, :ticket_category_id, :mute_role_id)''',
               {'guild_id': guild_id,
                'welcome_channel_id': welcome_channel_id,
                'cpr_channel_id': cpr_channel_id,
                'pr_settings_id': pr_settings_id,
                'mod_log_id': mod_log_id,
                'support_log_id': support_log_id,
                'ticket_category_id': ticket_category_id,
                'mute_role_id': mute_role_id})


@connection
def guild_settings(_c: Cursor, guild_id: int, prefix: str = None, color: hex = None,
                   welcome_messages: bool = False, leave_messages: bool = False,
                   welcome_dms: bool = False, welcome_dm: str = None) -> None:
    """
    Insert guild_settings to db.
    :param _c: Database cursor (provided by decorator)
    :param guild_id: Discord GuildID
    :param prefix: Prefix for the guild
    :param color: Color for the guild
    :param welcome_messages: Whether welcome messages are activated
    :param leave_messages: Whether leave messages are activated
    :param welcome_dms: Whether welcome direct messages are activated
    :param welcome_dm: The text that will be send to new members
    :return: None
    """
    # Parse bool into int
    welcome_messages = int(welcome_messages)
    leave_messages = int(leave_messages)

    # Insert into db
    _c.execute('''INSERT INTO guild_settings VALUES (:setting_id, :prefix, :color, 
                :welcome_messages, :leave_messages, :welcome_dms, :welcome_dm, :guild_id)''',
               {'setting_id': generate_new_id(table='guild_settings', identifier='setting_id'),
                'prefix': prefix,
                'color': color,
                'welcome_messages': welcome_messages,
                'leave_messages': leave_messages,
                'welcome_dms': welcome_dms,
                'welcome_dm': welcome_dm,
                'guild_id': guild_id
                })


@connection
def role(_c: Cursor, role_id: int, type_: str, guild_id: int) -> None:
    """
    Insert role into db.
    :param _c: Database cursor (provided by decorator)
    :param role_id: Discord RoleID
    :param type_: Type of role ("MODERATOR", "ADMIN" or "SUPPORTER")
    :param guild_id: Discord GuildID
    :return: None
    """
    # Check type_ for requirements
    if not (type_ == 'MODERATOR' or type_ == 'ADMIN' or type_ == 'SUPPORTER'):
        raise DatabaseAttributeError('type_', False, type_,
                                     "type_ has to be 'MODERATOR', 'ADMIN' or 'SUPPORTER'.")

    # Insert into db
    _c.execute('INSERT INTO roles VALUES (:role_id, :type, :guild_id)', {'role_id': role_id, 'type': type_,
                                                                         'guild_id': guild_id})


@connection
def ban(_c: Cursor, temp: bool, user_id: int, mod_id: int, date: datetime.datetime, guild_id: int, reason: str = None,
        until_date: datetime.datetime = None) -> None:
    """
    Insert ban into db.
    :param _c: Database cursor (provided by decorator)
    :param temp: Whether the ban is temporary
    :param user_id: Discord UserID
    :param mod_id: Discord UserID
    :param date: Date of ban
    :param guild_id: Discord GuildID
    :param reason: Reason for ban
    :param until_date: Date until the ban lasts
    :return: None
    """
    # Parse arguments into correct data types for db
    temp = int(temp)

    date = date.strftime('%Y-%m-%d %H:%M:%S')

    if until_date:
        until_date = until_date.strftime('%Y-%m-%d %H:%M:%S')

    # Insert into db
    _c.execute('INSERT INTO bans VALUES (:ban_id, :temp, :user_id, :mod_id, :reason, :date, :until_date, :guild_id)',
               {'ban_id': generate_new_id(table='bans', identifier='ban_id'),
                'temp': temp,
                'user_id': user_id,
                'mod_id': mod_id,
                'reason': reason,
                'date': date,
                'until_date': until_date,
                'guild_id': guild_id
                })


@connection
def mute(_c: Cursor, temp: bool, user_id: int, mod_id: int, date: datetime.datetime, guild_id: int, reason: str = None,
         until_date: datetime.datetime = None) -> None:
    """
    Insert ban into db.
    :param _c: Database cursor (provided by decorator)
    :param temp: Whether the mute is temporary
    :param user_id: Discord UserID
    :param mod_id: Discord UserID
    :param date: Date of mute
    :param guild_id: Discord GuildID
    :param reason: Reason for mute
    :param until_date: Date until the mute lasts
    :return: None
    """
    # Parse arguments into correct data types for db
    temp = int(temp)

    date = date.strftime('%Y-%m-%d %H:%M:%S')

    if until_date:
        until_date = until_date.strftime('%Y-%m-%d %H:%M:%S')

    # Insert into db
    _c.execute('INSERT INTO mutes VALUES (:mute_id, :temp, :user_id, :mod_id, :reason, :date, :until_date, :guild_id)',
               {'mute_id': generate_new_id(table='mutes', identifier='mute_id'),
                'temp': temp,
                'user_id': user_id,
                'mod_id': mod_id,
                'reason': reason,
                'date': date,
                'until_date': until_date,
                'guild_id': guild_id
                })


@connection
def warn(_c: Cursor, user_id: int, mod_id: int, date: datetime.datetime, guild_id: int, reason: str = None) -> None:
    """
    Insert ban into db.
    :param _c: Database cursor (provided by decorator)
    :param user_id: Discord UserID
    :param mod_id: Discord UserID
    :param date: Date of warn
    :param guild_id: Discord GuildID
    :param reason: Reason for warn
    :return: None
    """
    # Parse arguments into correct data types for db
    date = date.strftime('%Y-%m-%d %H:%M:%S')

    # Insert into db
    _c.execute('INSERT INTO warns VALUES (:warn_id, :user_id, :mod_id, :reason, :date, :guild_id)',
               {'warn_id': generate_new_id(table='warns', identifier='warn_id'),
                'user_id': user_id,
                'mod_id': mod_id,
                'reason': reason,
                'date': date,
                'guild_id': guild_id
                })


@connection
def report(_c: Cursor, reporter_id: int, user_id: int, date: datetime.datetime, guild_id: int,
           reason: str = None) -> None:
    """
    Insert report into db.
    :param _c: Database cursor (provided by decorator)
    :param reporter_id: Discord UserId
    :param user_id: Discord UserID
    :param date: Date of report
    :param guild_id: Discord GuildID
    :param reason: Reason for report
    :return: None
    """
    # Parse arguments into correct data types for db
    date = date.strftime('%Y-%m-%d %H:%M:%S')

    # Insert into db
    _c.execute('INSERT INTO reports VALUES (:report_id, :reporter_id, :user_id, :reason, :date, :guild_id)',
               {'report_id': generate_new_id(table='reports', identifier='report_id'),
                'reporter_id': reporter_id,
                'user_id': user_id,
                'reason': reason,
                'date': date,
                'guild_id': guild_id
                })


@connection
def private_room(_c: Cursor, room_channel_id: int, move_channel_id: int, owner_id: int, guild_id: int) -> None:
    """
    Insert private_room into db
    :param _c: Database cursor (provided by decorator)
    :param room_channel_id: Discord VoiceChannelID
    :param move_channel_id: Discord VoiceChannelID
    :param owner_id: Discord UserID
    :param guild_id: Discord UserID
    :return: None
    """

    # Insert into db
    _c.execute('INSERT INTO private_rooms VALUES (:room_id, :room_channel_id, :move_channel_id, :owner_id, :guild_id)',
               {'room_id': generate_new_id(table='private_rooms', identifier='room_id'),
                'room_channel_id': room_channel_id,
                'move_channel_id': move_channel_id,
                'owner_id': owner_id,
                'guild_id': guild_id
                })


@connection
def pr_settings(_c: Cursor, room_id: str) -> None:
    """
    Insert private room settings into db
    :param _c: Database cursor (provided by decorator)
    :param room_id: room_id (Table: private_rooms)
    :return: None
    """
    # TODO: Weitere Attribute hinzufügen (Zuerst in _manager._create_tables() hinzufügen)

    # Insert into db
    _c.execute('INSERT INTO pr_settings VALUES ({} , {})'.format(
        generate_new_id(table='pr_settings', identifier='pr_settings_id'),
        room_id))
    raise NotImplementedError()


@connection
def ticket(_c: Cursor, main_user_id: int, text_channel_id: int, guild_id: int, voice_channel_id: int = None,
           topic: str = None) -> None:
    """
    Insert support ticket into db
    :param _c: Database cursor (provided by decorator)
    :param main_user_id: Discord UserID of the user who created the ticket
    :param text_channel_id: Discord TextChannelID
    :param guild_id: Discord GuildID
    :param voice_channel_id: Discord VoiceChannel ID
    :param topic: Topic of the support ticket
    :return: None
    """

    # Insert ticket into db
    _c.execute('''INSERT INTO tickets VALUES (:ticket_id, :main_user_id, :text_channel_id, :voice_channel_id, 
                :topic, :guild_id)''',
               {'ticket_id': generate_new_id(table='tickets', identifier='ticket_id'),
                'main_user_id': main_user_id,
                'text_channel_id': text_channel_id,
                'voice_channel_id': voice_channel_id,
                'topic': topic,
                'guild_id': guild_id
                })


@connection
def ticket_user(_c: Cursor, user_id: int, ticket_id: str, is_mod: bool = False) -> None:
    """
    Insert ticket user into db
    :param _c: Database cursor (provided by decorator)
    :param user_id: Discord UserID
    :param ticket_id: From table tickets
    :param is_mod: Whether the user is a mod of the ticket
    :return: None
    """
    # Parse arguments into correct type
    is_mod = int(is_mod)

    # Insert ticket user into db
    _c.execute('INSERT INTO ticket_users VALUES (:user_id, :is_mod, :ticket_id)',
               {'user_id': user_id,
                'is_mod': is_mod,
                'ticket_id': ticket_id
                })
