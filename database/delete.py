from typing import Callable

from fryselBot.database._manager import connection
from sqlite3.dbapi2 import Cursor


def _delete_by_keyword_factory(table: str, keyword: str) -> Callable[[Cursor, str], None]:
    """
    Creates a function that deletes an entry in table by keyword
    :param table: Table to delete entry in
    :param keyword: Keyword for search condition
    :return: Function that deletes an entry in table by keyword
    """

    @connection
    def _delete_by_keyword(_c: Cursor, argument, **kwargs) -> None:
        """
        Deletes an entry in table by keyword
        :param _c: Database cursor (provided by decorator)
        :param argument: Value for keyword (search condition)
        :kwargs: Additional conditions
        """
        # Set up statement
        statement = "DELETE FROM {} WHERE {}=='{}'".format(table, keyword, argument)

        for k, v in kwargs.items():
            statement += " AND {}=='{}'".format(k, v)

        # Delete entry
        _c.execute(statement)

    return _delete_by_keyword


guild = _delete_by_keyword_factory(table='guilds', keyword='guild_id')

guild_settings = _delete_by_keyword_factory(table='guild_settings', keyword='guild_id')

role = _delete_by_keyword_factory(table='roles', keyword='role_id')

ban = _delete_by_keyword_factory(table='bans', keyword='ban_id')

mute = _delete_by_keyword_factory(table='mutes', keyword='mute_id')

warn = _delete_by_keyword_factory(table='warns', keyword='warn_id')

report = _delete_by_keyword_factory(table='reports', keyword='report_id')

private_room = _delete_by_keyword_factory(table='private_rooms', keyword='room_id')

pr_settings = _delete_by_keyword_factory(table='pr_settings', keyword='room_id')

ticket = _delete_by_keyword_factory(table='tickets', keyword='ticket_id')


@connection
def ticket_user(_c: Cursor, ticket_id: str, user_id: str) -> None:
    """
    Deletes an entry in table by keyword
    :param _c: Database cursor (provided by decorator)
    :param ticket_id: TicketID of the ticket_user
    :param user_id: UserID of the ticket_user
    """
    # Delete entry
    _c.execute("DELETE FROM ticket_users WHERE ticket_id=='{}' AND user_id=='{}'".format(ticket_id, user_id))


@connection
def warns_of_member(_c: Cursor, user_id: str, guild_id: str) -> None:
    """
    Deletes all warns of user on guild
    :param _c: Database cursor (provided by decorator)
    :param user_id: UserID of the warns
    :param guild_id: GuildID of the warns
    """
    # Delete entries
    _c.execute("DELETE FROM warns WHERE user_id=='{}' AND guild_id=='{}'".format(user_id, guild_id))


@connection
def all_entries_of_guild(_c: Cursor, guild_id: str) -> None:
    """
    Deletes everything related to guild_id out of database.
    :param _c: Database cursor (provided by decorator)
    :param guild_id: ID of guild that should be deleted
    """

    # Delete all pr_settings
    _c.execute('''DELETE FROM pr_settings
                WHERE room_id IN (
                    SELECT room_id FROM private_rooms
                    WHERE guild_id=='{}'
                )'''.format(guild_id))

    # Delete all ticket_users
    _c.execute('''DELETE FROM ticket_users
                    WHERE ticket_id IN (
                        SELECT ticket_id FROM tickets
                        WHERE guild_id=='{}'
                    )'''.format(guild_id))

    # Delete all entries of tables with guild_id attribute
    tables = ['guilds', 'guild_settings', 'roles', 'bans', 'mutes', 'warns', 'reports', 'private_rooms', 'tickets']

    for table in tables:
        _c.execute("DELETE FROM {} WHERE guild_id=='{}'".format(table, guild_id))
