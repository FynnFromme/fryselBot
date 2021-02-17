from datetime import datetime, timedelta
from fryselBot.database._manager import connection

###########################

# Refresh Database for test purposes
# _manager._delete_database()
# _manager._create_tables()

###########################

# Test code

now = datetime.now()
past = now - timedelta(hours=1)
future = now + timedelta(hours=1)


@connection
def f(_c):
    _c.execute("SELECT * FROM guilds")
    print(_c.fetchall())


f()

##########################
