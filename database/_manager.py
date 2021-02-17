import sqlite3
import os
from sqlite3.dbapi2 import Connection, Cursor


# Database errors

class DatabaseError(Exception):
    """Error within the database_manager"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args)


class DatabaseAttributeError(DatabaseError):
    """
    Error for attributes given the wrong way for db.

    Args:
        attribute_name  (str): Name of attribute that was given the wrong way
        type_error     (bool): Whether the type of the attribute was wrong
        argument        (Any): The argument that was provided for the attribute
        description     (str): Description of the error

    Attributes:
        attribute_name  (str): Name of attribute that was given the wrong way
        type_error     (bool): Whether the type of the attribute was wrong
        argument        (Any): The argument that was provided for the attribute
        description     (str): Description of the error
    """

    def __init__(self, attribute_name: str, type_error: bool, argument, description: str = None, *args, **kwargs):
        # Different error messages for type errors
        if type_error:
            error_message = "Wrong type given for {}. '{}' was given. {}".format(attribute_name, argument, description)
        else:
            error_message = "Wrong argument for {}. '{}' was given. {}".format(attribute_name, argument, description)

        super().__init__(error_message, *args, **kwargs)

        # Set attributes
        self.attribute_name = attribute_name
        self.type_error = type_error
        self.actual_parameter = argument
        self.description = description


class DatabaseEntryError(DatabaseError):
    """
    Error for not found entry while searching for keywords.

    Args:
        table      (str): Table that should have entry
        attribute  (str): Attribute that has no entry with keyword
        keyword    (Any): Keyword that was searched

    Attributes:
        table      (str): Table that should have entry
        attribute  (str): Attribute that has no entry with keyword
        keyword    (Any): Keyword that was searched
    """

    def __init__(self, table: str, attribute: str, keyword, conditions: dict = None, *args, **kwargs):
        error_message = "Did not found an entry '{}' for attribute(s) {}" \
                        " in table {}.\n Further conditions were: {}". \
            format(keyword, attribute, table, conditions)
        super().__init__(error_message, *args, **kwargs)


# Database function for internal use

def _delete_database() -> None:
    """
    Deletes the db (only for test purpose)
    :return: None
    """
    # Path of db file
    path = "/Users/fynn/Documents/Coding/PyCharm/fryselBot/bot.db"
    # Double check to not delete the wrong file
    if path.endswith("/Coding/PyCharm/fryselBot/bot.db"):
        # Try to delete file
        try:
            os.remove(path)
        except FileNotFoundError:  # File not found
            print("Database not deleted: FileNotFoundError")


def connection(func):
    """
    Handles db connection for functions
    :param func: Function that works with the db (first parameter should be for cursor)
    :return: None
    """

    def inner(*args, **kwargs):
        """Calls the function with db connection"""
        # Setup db connection
        _conn: Connection = sqlite3.connect("/Users/fynn/Documents/Coding/PyCharm/fryselBot/bot.db")

        # Create cursor to execute statements
        _c: Cursor = _conn.cursor()

        with _conn:
            # Call function
            return_value = func(_c, *args, **kwargs)
        _conn.close()

        return return_value

    return inner


@connection
def _create_tables(c: Cursor) -> None:
    """
    Setup db. (Only run once)
    :param c: Database cursor (provided by decorator)
    :return: None
    """

    """
    TABLE: guilds
    PRIMARY KEY: guild_id         # Discord Guild ID
    ATTRIBUTE: welcome_channel_id # Discord TextChannelID
    ATTRIBUTE: cpr_channel_id     # Discord VoiceChannelID
    ATTRIBUTE: pr_settings_id     # Discord TextChannelID
    ATTRIBUTE: mod_log_id         # Discord TextChannelID
    ATTRIBUTE: support_log_id     # Discord TextChannelID
    ATTRIBUTE: ticket_category_id # Discord CategoryID
    """
    c.execute("""CREATE TABLE guilds (
                    guild_id INTEGER PRIMARY KEY,
                    welcome_channel_id INTEGER,
                    cpr_channel_id INTEGER,
                    pr_settings_id INTEGER,
                    mod_log_id INTEGER,
                    support_log_id INTEGER,
                    ticket_category_id INTEGER
                    )""")

    """
    TABLE: guild_settings
    PRIMARY KEY: setting_id              # AUTOINCREMENT
    ATTRIBUTE: prefix
    ATTRIBUTE: primary_color             # hex as integer
    ATTRIBUTE: secondary_color           # hex as integer
    ATTRIBUTE: welcome_messages          # 0 or 1
    ATTRIBUTE: leave_messages            # 0 or 1
    FOREIGN KEY: guild_id  (guilds)
    """
    c.execute("""CREATE TABLE guild_settings (
                    setting_id TEXT PRIMARY KEY,
                    prefix TEXT,
                    primary_color INTEGER,
                    secondary_color INTEGER,
                    welcome_messages INTEGER,
                    leave_messages INTEGER,
                    guild_id TEXT NOT NULL,
                    FOREIGN KEY(guild_id) 
                        REFERENCES guilds (guild_id)
                    )""")

    """
    TABLE: roles
    PRIMARY KEY: role_id                 # Discord role id
    ATTRIBUTE: type                      # "ADMIN", "MOD", "MUTED" or "SUPPORT"
    FOREIGN KEY: guild_id  (guilds)
    """
    c.execute("""CREATE TABLE roles (
                    role_id INTEGER PRIMARY KEY,
                    type TEXT NOT NULL,
                    guild_id TEXT NOT NULL,
                    FOREIGN KEY (guild_id)
                        REFERENCES guilds (guild_id)
                    )""")

    """
    TABLE: bans
    PRIMARY KEY: ban_id                  # AUTOINCREMENT
    ATTRIBUTE: temp                      # 0 or 1
    ATTRIBUTE: user_id                   # Discord user id
    ATTRIBUTE: mod_id                    # Discord user id
    ATTRIBUTE: date                      # Date of ban
    ATTRIBUTE: until_date                # Until user is banned (if temp)
    ATTRIBUTE: reason
    FOREIGN KEY: guild_id  (guilds)
    """
    c.execute("""CREATE TABLE bans (
                    ban_id TEXT PRIMARY KEY,
                    temp INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    mod_id INTEGER NOT NULL,
                    reason TEXT,
                    date DATE NOT NULL,
                    until_date DATE,
                    guild_id TEXT NOT NULL,
                    FOREIGN KEY (guild_id)
                        REFERENCES guilds (guild_id)
                    )""")

    """
    TABLE: mutes
    PRIMARY KEY: mute_id                  # AUTOINCREMENT
    ATTRIBUTE: temp                      # 0 or 1
    ATTRIBUTE: user_id                   # Discord user id
    ATTRIBUTE: mod_id                    # Discord user id
    ATTRIBUTE: reason
    ATTRIBUTE: date                      # Date of mute
    ATTRIBUTE: until_date                # Until user is muted (if temp)
    FOREIGN KEY: guild_id  (guilds)
    """
    c.execute("""CREATE TABLE mutes (
                    mute_id TEXT PRIMARY KEY,
                    temp INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    mod_id INTEGER NOT NULL,
                    reason TEXT,
                    date DATE NOT NULL,
                    until_date DATE,
                    guild_id TEXT NOT NULL,
                    FOREIGN KEY (guild_id)
                        REFERENCES guilds (guild_id)
                    )""")

    """
    TABLE: warns
    PRIMARY KEY: warn_id                 # AUTOINCREMENT
    ATTRIBUTE: user_id                   # Discord user id
    ATTRIBUTE: mod_id                    # Discord user id
    ATTRIBUTE: reason
    ATTRIBUTE: date                      # Date of warn
    FOREIGN KEY: guild_id  (guilds)
    """
    c.execute("""CREATE TABLE warns (
                    warn_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    mod_id INTEGER NOT NULL,
                    reason TEXT,
                    date DATE NOT NULL,
                    guild_id TEXT NOT NULL,
                    FOREIGN KEY (guild_id)
                        REFERENCES guilds (guild_id)
                    )""")

    """
    TABLE: reports
    PRIMARY KEY: report_id               # AUTOINCREMENT
    ATTRIBUTE: reporter_id               # Discord user id
    ATTRIBUTE: user_id                # Discord user id
    ATTRIBUTE: reason
    ATTRIBUTE: date                      # Date of reports
    FOREIGN KEY: guild_id  (guilds)
    """
    c.execute("""CREATE TABLE reports (
                    report_id TEXT PRIMARY KEY,
                    reporter_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    reason TEXT,
                    date DATE NOT NULL,
                    guild_id TEXT NOT NULL,
                    FOREIGN KEY (guild_id)
                        REFERENCES guilds (guild_id)
                    )""")

    """
    TABLE: private_rooms                 # Create Private Room voice channels
    PRIMARY KEY: room_id                 # AUTOINCREMENT
    ATTRIBUTE: room_channel_id           # Discord voice channel id
    ATTRIBUTE: move_channel_id           # Discord voice channel id
    ATTRIBUTE: owner_id                  # Discord user id
    FOREIGN KEY: guild_id  (guilds)
    """
    c.execute("""CREATE TABLE private_rooms (
                    room_id TEXT PRIMARY KEY,
                    room_channel_id INTEGER NOT NULL,
                    move_channel_id INTEGER NOT NULL,
                    owner_id INTEGER NOT NULL,
                    guild_id TEXT NOT NULL,
                    FOREIGN KEY (guild_id)
                        REFERENCES guilds (guild_id)
                    )""")

    # TODO: Weitere Attribute zu pr_settings hinzufügen
    """
    TABLE: pr_settings                   # Settings for private rooms
    PRIMARY KEY: pr_settings_id          # AUTOINCREMENT
    ATTRIBUTE: ...
    FOREIGN KEY: room_id  (private_rooms)
    """
    c.execute("""CREATE TABLE pr_settings (
                    pr_settings_id TEXT PRIMARY KEY,
                    
                    room_id INTEGER NOT NULL,
                    FOREIGN KEY (room_id)
                        REFERENCES private_rooms (room_id)
                    )""")

    """
    TABLE: tickets                       # Support ticket
    PRIMARY KEY: ticket_id               # AUTOINCREMENT
    ATTRIBUTE: user_id                   # Discord user id
    ATTRIBUTE: text_channel_id           # Discord text channel id
    ATTRIBUTE: voice_channel_id          # Discord voice channel id
    ATTRIBUTE: topic
    FOREIGN KEY: guild_id  (guilds)
    """
    c.execute("""CREATE TABLE tickets (
                    ticket_id TEXT PRIMARY KEY,
                    main_user_id INTEGER NOT NULL,
                    text_channel_id INTEGER NOT NULL,
                    voice_channel_id INTEGER,
                    topic TEXT,
                    guild_id TEXT NOT NULL,
                    FOREIGN KEY (guild_id)
                        REFERENCES guilds (guild_id)
                    )""")

    """
    TABLE: ticket_users
    PRIMARY KEY: relation_id            # AUTOINCREMENT
    ATTRIBUTE: user_id                  # Discord UserID
    ATTRIBUTE: is_mod                   # 0 or 1
    ATTRIBUTE: ticket_id                # (Table tickets: ticket_id)
    """
    c.execute("""CREATE TABLE ticket_users (
                    user_id INTEGER,
                    is_mod INTEGER,
                    ticket_id TEXT,
                    FOREIGN KEY (ticket_id)
                        REFERENCES tickets (ticket_id)
                    )""")
