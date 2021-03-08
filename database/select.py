from fryselBot.database._manager import connection, DatabaseEntryError, DatabaseError
from sqlite3.dbapi2 import Cursor
from datetime import datetime
from fryselBot import utilities as util


def _select_by_guild_id_factory(table: str, attribute: str, all_entries: bool = False, **kwargs):
    """
    Create functions that return a value or list of values (if all) out of the db by the conditions represented
    by kwargs.
    :param table: Table to search in
    :param attribute: Attribute out of table
    :param all_entries: Whether all entries should
    :param kwargs: Further conditions for selecting the values (Example: {"id": 1} -> WHERE ... AND 'id' = 1)
    :return: Function that returns a single value or list of values (if all) out of the db by the GuildID
    """

    @connection
    def _select_by_guild_id(_c: Cursor, guild_id: int):
        """
        Get first value out of db by the guild_id and further conditions
        Throws an error when a single value is required and there are no entries matching the conditions.
        :param _c: Database cursor (provided by decorator)
        :param guild_id: Value for GuildID
        :return: Server invite
        """
        # Prepare sql statement
        statement = "SELECT {} FROM {} WHERE guild_id=='{}'".format(attribute, table, guild_id)

        # Add further conditions of given by kwargs
        for k, v in kwargs.items():
            statement += " AND {}='{}'".format(k, v)

        if not all_entries:
            statement += " LIMIT 1"

        # Fetch invite out of db
        _c.execute(statement)

        # Try to get value
        try:
            if all_entries:  # Get all values
                entries = _c.fetchall()
                # Put all values in a list
                value = []
                for e in entries:
                    value.append(e[0])
            else:  # Get the first value
                value = _c.fetchone()[0]

        except TypeError:  # Throw error when there is no single value
            raise DatabaseEntryError(table, attribute, guild_id, conditions=kwargs)

        return value

    # Return closure
    return _select_by_guild_id


@connection
def _fetch_mod_operation_entry(_c: Cursor, guild_id: int, user_id: int, table: str, id_identifier: str,
                               operation_id: str = None) -> tuple:
    """
    Fetch the latest mod operation of the user_id on the guild_id or by operation_id
    :param _c: Database Cursor (provided by decorator)
    :param guild_id: Discord GuildID
    :param user_id: Discord UserID
    :param table: Table to search in
    :param id_identifier: The identifier of the mod operation ID
    :param operation_id: The argument to search for
    :return: Database entry as tuple
    """
    if operation_id:
        # Fetch entry by operation_id out of database
        _c.execute("SELECT * FROM {} WHERE guild_id=='{}' AND user_id=='{}' AND {}=='{}' LIMIT 1".format(table,
                                                                                                         guild_id,
                                                                                                         user_id,
                                                                                                         id_identifier,
                                                                                                         operation_id))
        entry = _c.fetchone()
        # Check if there was a operation on the user
        if not entry:
            raise DatabaseEntryError(table=table, attribute=id_identifier, keyword=operation_id,
                                     conditions={"guild_id": guild_id, "user_id": user_id})

    else:
        # Fetch latest entry
        _c.execute("""SELECT * FROM {} t
                    inner join (
                        SELECT {}, MAX(date) as MaxDate
                        FROM {}
                        WHERE guild_id=='{}' AND user_id=='{}'
                        GROUP BY guild_id
                     ) tm on t.{} = tm.{} AND t.date = tm.MaxDate""".format(table,
                                                                            id_identifier,
                                                                            table,
                                                                            guild_id,
                                                                            user_id,
                                                                            id_identifier,
                                                                            id_identifier))
        entry = _c.fetchone()

        # Check if there was a operation on the user
        if not entry:
            raise DatabaseEntryError(table=table, attribute="guild_id, user_id",
                                     keyword="{}', '{}".format(guild_id, user_id))

    return entry


welcome_channel_id = _select_by_guild_id_factory(table="guilds", attribute="welcome_channel_id")

cpr_channel_id = _select_by_guild_id_factory(table="guilds", attribute="cpr_channel_id")

pr_settings_id = _select_by_guild_id_factory(table="guilds", attribute="pr_settings_id")

mod_log_id = _select_by_guild_id_factory(table="guilds", attribute="mod_log_id")

support_log_id = _select_by_guild_id_factory(table="guilds", attribute="support_log_id")

ticket_category_id = _select_by_guild_id_factory(table="guilds", attribute="ticket_category_id")

prefix = _select_by_guild_id_factory(table="guild_settings", attribute="prefix")

color = _select_by_guild_id_factory(table="guild_settings", attribute="color")

welcome_messages = _select_by_guild_id_factory(table="guild_settings", attribute="welcome_messages")

leave_messages = _select_by_guild_id_factory(table="guild_settings", attribute="leave_messages")

welcome_dms = _select_by_guild_id_factory(table="guild_settings", attribute="welcome_dms")

welcome_dm = _select_by_guild_id_factory(table="guild_settings", attribute="welcome_dm")

moderator_roles = _select_by_guild_id_factory(table="roles", attribute="role_id", all_entries=True, type="MODERATOR")

mute_role = _select_by_guild_id_factory(table="roles", attribute="role_id", all_entries=False, type="MUTE")

support_roles = _select_by_guild_id_factory(table="roles", attribute="role_id", all_entries=True, type="SUPPORTER")

admin_roles = _select_by_guild_id_factory(table="roles", attribute="role_id", all_entries=True, type="ADMIN")


@connection
def all_guilds(_c: Cursor) -> list:
    """
    Creates a list of all guilds IDs in database
    :param _c: Database cursor (provided by decorator)
    :return: List of all guild IDs in database
    """
    # Fetch all guilds
    _c.execute("SELECT guild_id FROM guilds")
    guilds = _c.fetchall()
    # Select guild_ids
    guilds = list(map(lambda entry: entry[0], guilds))

    return guilds


@connection
def all_welcome_channels(_c: Cursor) -> list:
    """
    Creates a list of all pairs of welcome channel IDs and guild_ids in database
    :param _c: Database cursor (provided by decorator)
    :return: List of all pairs of welcome channel IDs and guild_ids in database
    """
    # Fetch all welcome channels and belonging guild_ids
    _c.execute("SELECT welcome_channel_id, guild_id FROM guilds")
    channels = _c.fetchall()
    # Select pairs of welcome_channel_id and guild_id
    channels = list(map(lambda entry: entry[:2], channels))

    return channels


@connection
def all_roles(_c: Cursor) -> list:
    """
    Creates a list of all pairs of role IDs and guild_ids in database
    :param _c: Database cursor (provided by decorator)
    :return: List of all pairs of role IDs and guild_ids in database
    """
    # Fetch all role_ids and belonging guild_ids
    _c.execute("SELECT role_id, guild_id FROM roles")
    roles = _c.fetchall()
    # Select pairs of role_id and guild_id
    roles = list(map(lambda entry: entry[:2], roles))

    return roles


class Ban:
    """
    Ban object that represents a selected ban entry out of the database.
    Args:
        guild_id         (int): GuildID of the ban
        user_id          (int): ID of the banned user
        ban_id           (str): Internally BanID
    Attributes:
        ban_id           (str): Internally BanID
        temp            (bool): Whether the ban is temporary
        user_id          (int): ID of the banned user
        mod_id           (int): ID of the moderator, who executed the ban
        reason           (str): Reason of the ban
        date        (datetime): Date of the ban
        until_date  (datetime): Date up to which the user is banned
        guild_id         (int): ID of the guild where the ban took place
    """

    def __init__(self, guild_id: int, user_id: int, ban_id: str = None):
        # Fetch ban entry out of database
        ban = _fetch_mod_operation_entry(guild_id=guild_id, user_id=user_id, table="bans", id_identifier="ban_id",
                                         operation_id=ban_id)

        # Create Attributes of Ban object
        self._ban_id = ban[0]
        self._temp = bool(ban[1])
        self._user_id = ban[2]
        self._mod_id = ban[3]
        self._reason = ban[4]
        self._date = util.iso_to_datetime(ban[5])
        self._until_date = util.iso_to_datetime(ban[6])
        self._guild_id = ban[7]

    # Add properties
    ban_id = property(lambda self: self._ban_id)
    temp = property(lambda self: self._temp)
    user_id = property(lambda self: self._user_id)
    mod_id = property(lambda self: self._mod_id)
    reason = property(lambda self: self._reason)
    date = property(lambda self: self._date)
    until_date = property(lambda self: self._until_date)
    guild_id = property(lambda self: self._guild_id)


@connection
def expired_bans(_c: Cursor) -> list:
    """
    Creates a list of expired temporary bans
    :param _c: Database cursor (provided by decorator)
    :return: List of expired temporary bans
    """
    # Current datetime for comparison
    now = datetime.now()

    # Fetch all bans that are expired
    _c.execute("SELECT guild_id, user_id, ban_id FROM bans WHERE temp==1 AND until_date <= Datetime('{}')".format(
        now.strftime("%Y-%m-%d %H:%M:%S")))
    entries = _c.fetchall()

    # Create a list of expired Ban objects
    bans = []
    for ban in entries:
        bans.append(Ban(guild_id=ban[0], user_id=ban[1], ban_id=ban[2]))

    return bans


class Mute:
    """
    Represents either the latest mute of user_id on guild_id or a specific mute by mute_id.
    Args:
        guild_id         (int): GuildID of the mute
        user_id          (int): ID of the muted user
        mute_id          (str): Internally MuteID
    Attributes:
        mute_id          (str): Internally MuteID
        temp            (bool): Whether the mute is temporary
        user_id          (int): ID of the muted user
        mod_id           (int): ID of the moderator, who executed the mute
        reason           (str): Reason of the mute
        date        (datetime): Date of the mute
        until_date  (datetime): Date up to which the user is muted
        guild_id         (int): ID of the guild where the mute took place
    """

    def __init__(self, guild_id: int, user_id: int, mute_id: str = None):
        # Fetch mute entry out of database
        mute = _fetch_mod_operation_entry(guild_id=guild_id, user_id=user_id, table="mutes", id_identifier="mute_id",
                                          operation_id=mute_id)

        # Create Attributes of Mute object
        self._mute_id = mute[0]
        self._temp = bool(mute[1])
        self._user_id = mute[2]
        self._mod_id = mute[3]
        self._reason = mute[4]
        self._date = util.iso_to_datetime(mute[5])
        self._until_date = util.iso_to_datetime(mute[6])
        self._guild_id = mute[7]

    # Add properties
    mute_id = property(lambda self: self._mute_id)
    temp = property(lambda self: self._temp)
    user_id = property(lambda self: self._user_id)
    mod_id = property(lambda self: self._mod_id)
    reason = property(lambda self: self._reason)
    date = property(lambda self: self._date)
    until_date = property(lambda self: self._until_date)
    guild_id = property(lambda self: self._guild_id)


@connection
def expired_mutes(_c: Cursor) -> list:
    """
    Creates a list of expired temporary mutes
    :param _c: Database cursor (provided by decorator)
    :return: List of expired temporary mutes
    """
    # Current datetime for comparison
    now = datetime.now()

    # Fetch all mutes that are expired
    _c.execute("SELECT guild_id, user_id, mute_id FROM mutes WHERE temp==1 AND until_date <= Datetime('{}')".format(
        now.strftime("%Y-%m-%d %H:%M:%S")))
    entries = _c.fetchall()

    # Create a list of expired Ban objects
    mutes = []
    for mute in entries:
        mutes.append(Mute(guild_id=mute[0], user_id=mute[1], mute_id=mute[2]))

    return mutes


class Warn:
    """
    Represents either the latest warn of user_id on guild_id or a specific warn by warn_id.
    Args:
        guild_id         (int): Discord GuildID
        user_id          (int): Discord UserID
        warn_id          (str): Internally WarnID
    Attributes:
        warn_id          (str): Internally WarnID
        user_id          (int): ID of the warned user
        mod_id           (int): ID of the moderator, who executed the warn
        reason           (str): Reason of the warn
        date        (datetime): Date of the warn
        guild_id         (int): ID of the guild where the warn took place
    """

    def __init__(self, guild_id: int, user_id: int, warn_id: str = None):
        # Fetch warn entry out of database
        warn = _fetch_mod_operation_entry(guild_id=guild_id, user_id=user_id, table="warns", id_identifier="warn_id",
                                          operation_id=warn_id)

        # Create Attributes of Warn object
        self._warn_id = warn[0]
        self._user_id = warn[1]
        self._mod_id = warn[2]
        self._reason = warn[3]
        self._date = util.iso_to_datetime(warn[4])
        self._guild_id = warn[5]

    # Add properties
    warn_id = property(lambda self: self._warn_id)
    user_id = property(lambda self: self._user_id)
    mod_id = property(lambda self: self._mod_id)
    reason = property(lambda self: self._reason)
    date = property(lambda self: self._date)
    guild_id = property(lambda self: self._guild_id)


@connection
def warns_of_user(_c: Cursor, user_id: int, guild_id: int, count: int = 5) -> list:
    """
    Selects the latest warns of user_id on guild_id
    :param _c: Database cursor (provided by decorator)
    :param user_id: Discord UserID
    :param guild_id: Discord GuildID
    :param count: Count of warns that are selected
    :return: List of the latest count warns of user_id on guild_id
    """
    # Fetch latest count warns of user_id on guild_id
    _c.execute("""SELECT guild_id, user_id, warn_id FROM warns WHERE guild_id=='{}' AND user_id=='{}' 
                ORDER BY warn_id DESC LIMIT {}""".format(guild_id, user_id, count))

    entries = _c.fetchall()

    # Create list of Warn objects
    warns = []
    for warn in entries:
        warns.append(Warn(guild_id=warn[0], user_id=warn[1], warn_id=warn[2]))

    return warns


class Report:
    """
    Represents either the latest report of user_id on guild_id or a specific warn by report_id.
    Args:
        user_id          (int): Discord UserID
        guild_id         (int): Discord GuildID
        report_id        (str): Internally ReportID
    Attributes:
        report_id        (str): Internally ReportID
        reporter_id      (int): ID of the user that reported
        user_id          (int): ID of the reported user
        reason           (str): Reason of the report
        date        (datetime): Date of the report
        guild_id         (int): ID of the guild where the report took place
    """
    def __init__(self, user_id: int, guild_id: int, report_id: str = None):
        # Fetch report entry out of database
        report = _fetch_mod_operation_entry(guild_id=guild_id, user_id=user_id, table="reports",
                                            id_identifier="report_id", operation_id=report_id)

        self._report_id = report[0]
        self._reporter_id = report[1]
        self._user_id = report[2]
        self._reason = report[3]
        self._date = report[4]
        self._guild_id = report[5]

    # Add properties
    report_id = property(lambda self: self._report_id)
    reporter_id = property(lambda self: self._reporter_id)
    user_id = property(lambda self: self._user_id)
    reason = property(lambda self: self._reason)
    date = property(lambda self: self._date)
    guild_id = property(lambda self: self._guild_id)


class PrivateRoom:
    """
    Represents private room.
    Args:
        One of owner_id and room_channel_id must be given.
        guild_id         (int): Discord GuildID
        owner_id         (int): Discord User ID
        room_channel_id  (str): Discord VoiceChannelID
    Attributes:
        room_id          (str): Internally room ID
        room_channel_id  (int): ID of the pr voice channel
        move_channel_id  (int): ID of the move voice channel
        owner_id         (int): ID of the owner from the server
        guild_id         (int): ID of the guild of the private room
        ...
    """
    def __init__(self, guild_id: int, owner_id: int = None, room_channel_id: int = None):
        # Fetch private room entry out of database
        if owner_id:
            # Get private room entry by owner_id
            @connection
            def execution(_c: Cursor):
                _c.execute("SELECT * FROM private_rooms WHERE guild_id=='{}' AND owner_id=='{}' LIMIT 1".format(
                    guild_id,
                    owner_id))
                return _c.fetchone()

            entry = execution()

            # Check if there is a private room of the user
            if not entry:
                raise DatabaseEntryError(table="private_rooms", attribute="owner_id", keyword=owner_id,
                                         conditions={"guild_id": guild_id})
        elif room_channel_id:
            # Get private room entry by room_channel_id
            @connection
            def execution(_c: Cursor):
                _c.execute("SELECT * FROM private_rooms WHERE guild_id=='{}' AND room_channel_id=='{}' LIMIT 1".format(
                    guild_id,
                    room_channel_id))
                return _c.fetchone()

            entry = execution()

            # Check if there is a private room with the channel_id
            if not entry:
                raise DatabaseEntryError(table="private_rooms", attribute="room_channel_id", keyword=room_channel_id,
                                         conditions={"guild_id": guild_id})
        else:
            # Throw exception because there were not enough information about the room
            raise DatabaseError("""Error while initializing PrivateRoom object. At least one of owner_id or 
            room_channel_id has to be given""")

        # Initializing attributes
        self._room_id = entry[0]
        self._room_channel_id = entry[1]
        self._move_channel_id = entry[2]
        self._owner_id = entry[3]
        self._guild_id = entry[4]

        # Fetch private room settings entry
        @connection
        def execution(_c: Cursor):
            _c.execute("SELECT * FROM pr_settings WHERE room_id=='{}'LIMIT 1".format(self.room_id))
            return _c.fetchone()

        settings = execution()

        # Initializing settings attributes
        # TODO: Add pr settings

    # Add properties
    room_id = property(lambda self: self._room_id)
    room_channel_id = property(lambda self: self._room_channel_id)
    move_channel_id = property(lambda self: self._move_channel_id)
    owner_id = property(lambda self: self._owner_id)
    guild_id = property(lambda self: self._guild_id)


class Ticket:
    """
    Represents a support ticket.
    Args:
        guild_id          (int): Discord GuildID
        ticket_id         (str): Internally ticket ID
        text_channel_id   (int): Discord TextChannelID
        voice_channel_id  (int): Discord VoiceChannelID
    Attributes:
        ticket_id         (str): Internally ticket ID
        main_user_id      (int): ID from the user who created the ticket
        text_channel_id   (int): TextChannelID of the ticket
        voice_channel_id  (int): VoiceChannelID of the ticket
        topic             (str): Topic of the ticket
        guild_id          (str): GuildID of the ticket
        user_ids       (list[int]): List of userIDs who have access to the ticket
        mod_ids        (list[int]): List of modIDs responsible for the ticket
    """
    def __init__(self, guild_id: int, ticket_id: str = None, text_channel_id: int = None, voice_channel_id: int = None):
        if ticket_id:
            # Fetch ticket entry by ticket_id
            @connection
            def execution(_c: Cursor):
                _c.execute("SELECT * FROM tickets WHERE guild_id=='{}' AND ticket_id=='{}' LIMIT 1".format(
                    guild_id,
                    ticket_id))
                return _c.fetchone()

            entry = execution()

            # Check if there is a ticket with the channel_id
            if not entry:
                raise DatabaseEntryError(table="tickets", attribute="ticket_id", keyword=ticket_id,
                                         conditions={"guild_id": guild_id})
        elif text_channel_id:
            # Fetch ticket entry by text_channel_id
            @connection
            def execution(_c: Cursor):
                _c.execute("SELECT * FROM tickets WHERE guild_id=='{}' AND text_channel_id=='{}' LIMIT 1".format(
                    guild_id,
                    text_channel_id))
                return _c.fetchone()

            entry = execution()

            # Check if there is a ticket with the channel_id
            if not entry:
                raise DatabaseEntryError(table="tickets", attribute="text_channel_id", keyword=text_channel_id,
                                         conditions={"guild_id": guild_id})
        elif voice_channel_id:
            # Fetch ticket entry by voice_channel_id
            @connection
            def execution(_c: Cursor):
                _c.execute("SELECT * FROM tickets WHERE guild_id=='{}' AND voice_channel_id=='{}' LIMIT 1".format(
                    guild_id,
                    voice_channel_id))
                return _c.fetchone()

            entry = execution()

            # Check if there is a ticket with the channel_id
            if not entry:
                raise DatabaseEntryError(table="tickets", attribute="voice_channel_id", keyword=voice_channel_id,
                                         conditions={"guild_id": guild_id})
        else:
            # Throw exception because there were not enough information about the ticket
            raise DatabaseError("""Error while initializing Ticket object. At least one of ticket_id, text_channel_id or 
            voice_channel_id has to be given""")

        # Initializing attributes
        self._ticket_id = entry[0]
        self._main_user_id = entry[1]
        self._text_channel_id = entry[2]
        self._voice_channel_id = entry[3]
        self._topic = entry[4]
        self._guild_id = entry[5]

        # Fetch users of ticket
        @connection
        def execution(_c: Cursor):
            _c.execute("SELECT user_id FROM ticket_users WHERE ticket_id=='{}' AND is_mod==0".format(self.ticket_id))
            return _c.fetchall()

        self._user_ids = list(map(lambda x: x[0], execution()))

        # Fetch mods of ticket
        @connection
        def execution(_c: Cursor):
            _c.execute("SELECT user_id FROM ticket_users WHERE ticket_id=='{}' AND is_mod==1".format(self.ticket_id))
            return _c.fetchall()

        self._mod_ids = list(map(lambda x: x[0], execution()))

    # Add properties
    ticket_id = property(lambda self: self._ticket_id)
    main_user_id = property(lambda self: self._main_user_id)
    text_channel_id = property(lambda self: self._text_channel_id)
    voice_channel_id = property(lambda self: self._voice_channel_id)
    topic = property(lambda self: self._topic)
    guild_id = property(lambda self: self._guild_id)
    user_ids = property(lambda self: self._user_ids)
    mod_ids = property(lambda self: self._mod_ids)
