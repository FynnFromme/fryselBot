from typing import Callable, Any

from fryselBot.database.manager import connection
from sqlite3.dbapi2 import Cursor


def _update_by_keyword_factory(table: str, attribute: str, keyword: str) -> Callable[[Cursor, str, Any], None]:
    """
    Create functions that updates attribute in table by guild_id.
    :param table: Table to update attribute in
    :param attribute: Attribute out of table
    :param keyword: Attribute that is the condition
    :return: Function that updates attribute in table by guild_id
    """

    @connection
    def update_by_keyword_id(_c: Cursor, argument: int, value=None) -> None:
        """
        Updates the attribute in the table to value by guild_id.
        :param _c: Database cursor (provided by decorator)
        :param value: New value for the attribute
        :param argument: Value for keyword (search condition)
        :return: None
        """
        if type(value) == bool:
            value = int(value)

        # Update the attribute in table
        if value is not None:  # Set to value if value != None
            _c.execute(f"UPDATE {table} SET {attribute}=? WHERE {keyword}==?", (value, argument))
        else:  # Set to NULL if value == None
            _c.execute(f"UPDATE {table} SET {attribute}=NULL WHERE {keyword}==?", (argument,))

    return update_by_keyword_id


welcome_channel_id = _update_by_keyword_factory(table='guilds', attribute='welcome_channel_id', keyword='guild_id')

cpr_channel_id = _update_by_keyword_factory(table='guilds', attribute='cpr_channel_id', keyword='guild_id')

pr_settings_id = _update_by_keyword_factory(table='guilds', attribute='pr_settings_id', keyword='guild_id')

pr_categroy_id = _update_by_keyword_factory(table='guilds', attribute='pr_category_id', keyword='guild_id')

mod_log_id = _update_by_keyword_factory(table='guilds', attribute='mod_log_id', keyword='guild_id')

support_log_id = _update_by_keyword_factory(table='guilds', attribute='support_log_id', keyword='guild_id')

ticket_category_id = _update_by_keyword_factory(table='guilds', attribute='ticket_category_id', keyword='guild_id')

mute_role_id = _update_by_keyword_factory(table='guilds', attribute='mute_role_id', keyword='guild_id')

prefix = _update_by_keyword_factory(table='guild_settings', attribute='prefix', keyword='guild_id')

color = _update_by_keyword_factory(table='guild_settings', attribute='color', keyword='guild_id')

welcome_messages = _update_by_keyword_factory(table='guild_settings', attribute='welcome_messages', keyword='guild_id')

leave_messages = _update_by_keyword_factory(table='guild_settings', attribute='leave_messages', keyword='guild_id')

welcome_dms = _update_by_keyword_factory(table='guild_settings', attribute='welcome_dms', keyword='guild_id')

welcome_dm = _update_by_keyword_factory(table='guild_settings', attribute='welcome_dm', keyword='guild_id')

pr_owner_id = _update_by_keyword_factory(table='private_rooms', attribute='owner_id', keyword='room_id')

pr_move_channel_id = _update_by_keyword_factory(table='private_rooms', attribute='move_channel_id', keyword='room_id')

pr_name = _update_by_keyword_factory(table='pr_settings', attribute='name', keyword='room_id')

pr_game_activity = _update_by_keyword_factory(table='pr_settings', attribute='game_activity', keyword='room_id')

pr_locked = _update_by_keyword_factory(table='pr_settings', attribute='locked', keyword='room_id')

pr_user_limit = _update_by_keyword_factory(table='pr_settings', attribute='user_limit', keyword='room_id')

pr_hidden = _update_by_keyword_factory(table='pr_settings', attribute='hidden', keyword='room_id')

default_pr_name = _update_by_keyword_factory(table='default_pr_settings', attribute='name', keyword='guild_id')

default_pr_game_activity = _update_by_keyword_factory(table='default_pr_settings', attribute='game_activity',
                                                      keyword='guild_id')

default_pr_locked = _update_by_keyword_factory(table='default_pr_settings', attribute='locked', keyword='guild_id')

default_pr_user_limit = _update_by_keyword_factory(table='default_pr_settings', attribute='user_limit',
                                                   keyword='guild_id')

default_pr_hidden = _update_by_keyword_factory(table='default_pr_settings', attribute='hidden', keyword='guild_id')

voice_channel_id = _update_by_keyword_factory(table='tickets', attribute='voice_channel_id', keyword='ticket_id')

response = _update_by_keyword_factory(table='waiting_for_responses', attribute='response', keyword='id')
