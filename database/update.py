from fryselBot.database._manager import connection
from sqlite3.dbapi2 import Cursor


def _update_by_keyword_factory(table: str, attribute: str, keyword: str):
    """
    Create functions that updates attribute in table by guild_id.
    :param table: Table to update attribute in
    :param attribute: Attribute out of table
    :param keyword: Attribute that is the condition
    :return: Function that updates attribute in table by guild_id
    """

    @connection
    def update_by_keyword_id(_c: Cursor, value: str, argument) -> None:
        """
        Updates the attribute in the table to value by guild_id.
        :param _c: Database cursor (provided by decorator)
        :param value: New value for the attribute
        :param argument: Value for keyword (search condition)
        :return: None
        """
        # Update the attribute in table
        if value:  # Set to value if value != None
            _c.execute("UPDATE {} SET {}='{}' WHERE {}=='{}'".format(table, attribute, value, keyword, argument))
        else:  # Set to NULL if value == None
            _c.execute("UPDATE {} SET {}=NULL WHERE {}=='{}'".format(table, attribute, keyword, argument))

    return update_by_keyword_id


welcome_channel_id = _update_by_keyword_factory(table="guilds", attribute="welcome_channel_id", keyword="guild_id")

cpr_channel_id = _update_by_keyword_factory(table="guilds", attribute="cpr_channel_id", keyword="guild_id")

pr_settings_id = _update_by_keyword_factory(table="guilds", attribute="pr_settings_id", keyword="guild_id")

mod_log_id = _update_by_keyword_factory(table="guilds", attribute="mod_log_id", keyword="guild_id")

support_log_id = _update_by_keyword_factory(table="guilds", attribute="support_log_id", keyword="guild_id")

ticket_category_id = _update_by_keyword_factory(table="guilds", attribute="ticket_category_id", keyword="guild_id")

prefix = _update_by_keyword_factory(table="guild_settings", attribute="prefix", keyword="guild_id")

primary_color = _update_by_keyword_factory(table="guild_settings", attribute="primary_color", keyword="guild_id")

secondary_color = _update_by_keyword_factory(table="guild_settings", attribute="secondary_color", keyword="guild_id")

welcome_messages = _update_by_keyword_factory(table="guild_settings", attribute="welcome_messages", keyword="guild_id")

leave_messages = _update_by_keyword_factory(table="guild_settings", attribute="leave_messages", keyword="guild_id")

owner_id = _update_by_keyword_factory(table="private_rooms", attribute="owner_id", keyword="room_id")

voice_channel_id = _update_by_keyword_factory(table="tickets", attribute="voice_channel_id", keyword="ticket_id")
