# discord.py imports
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord import Message

# fryselBot imports
from database import delete
from system.private_rooms import private_rooms
from system import cogs, guilds, appearance, help

try:
    from utilities import secret
except ModuleNotFoundError:
    # /utilities/secrept.py is missing
    print('\033[31mFatal Error: /utilities/secret.py is missing.\nPlease read step 6 of https://github.com/Fynn-F/fryselBot#usage\033[0m')
    exit()


async def get_prefix(_: Bot, message: Message):
    """Returns the prefix for the guild of the message"""
    return appearance.get_prefix(guild_id=message.guild.id)


# Setup intents and create bot client
intents = discord.Intents.all()
client = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None, case_insensitive=True)

# Load all extensions
cogs.load_all(client)


@client.event
async def on_ready():
    """Called when the client is starting"""
    # Set presence of bot
    await client.change_presence(status=discord.Status.online)
    change_status.start()

    # Set database up to date
    for check in guilds.checks:
        check(client)

    for check in guilds.async_checks:
        await check(client)

    delete.all_waiting_for_responses()

    # States, that the bot is ready
    print(f'\033[93m{appearance.bot_name} is logged in as user {client.user.name}\033[0m')


@tasks.loop(seconds=30)
async def change_status():
    """Set the status of bot. Cycles through multiple status over time."""
    await client.change_presence(activity=discord.Game(next(appearance.status)))


@client.event
async def on_message(message: Message):
    """Is called when there is a new message in a text channel."""
    if message.author.bot:
        # Ignore messages from bots
        return
    elif message.guild is None:
        # Private messages
        pass
    elif private_rooms.is_settings_channel(message.channel):
        # Ignore messages in settings channel
        return
    elif message.content == appearance.default_prefix + 'help':
        # Default help command
        await help.help_command(message)
    else:
        # Guild messages
        await client.process_commands(message)


# Starts the bot with given token
client.run(secret.bot_token)
