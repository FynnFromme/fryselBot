from fryselBot.database import _manager, insert, update, select

# # Reset Database
# _manager._delete_database()
# _manager._create_tables()
#
# # Setup for test server
guild_id = 800167075636445264
#
# insert.guild(guild_id=guild_id)
# insert.guild_settings(guild_id=guild_id)
# insert.role(role_id=808448742964330506, type_="ADMIN", guild_id=guild_id)
# insert.role(role_id=808457427800162334, type_="MOD", guild_id=guild_id)
# update.prefix(value="-", argument=guild_id)
# update.welcome_messages(value=True, argument=guild_id)
# update.leave_messages(value=True, argument=guild_id)
# update.welcome_channel_id(value=810258839718199296, argument=guild_id)


@_manager.connection
def f(_c):
    _c.execute("SELECT * FROM guilds")
    print("Guilds: ", _c.fetchall())
    _c.execute("SELECT * FROM guild_settings")
    print("GuildSettings: ", _c.fetchall())


f()

print("Refreshed Database")