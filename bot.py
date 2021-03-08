# discord.py imports
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord import Message

# fryselBot imports
from fryselBot.system import help, appearance, guilds, cogs
from fryselBot.utilities import secret, util


async def get_prefix(bot: Bot, message: Message):
    """Returns the prefix for the guild of the message"""
    return appearance.get_prefix(guild_id=message.guild.id)


# Setup intents and create bot client
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
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

    # States, that the bot is ready
    print("{} is logged in as user {}".format(appearance.bot_name, client.user.name))


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
    elif message.content == appearance.default_prefix + "help":
        # Default help command
        await help.help_command(message)
    elif message.guild is None:
        # Private messages
        pass
    else:
        # Guild messages
        await client.process_commands(message)


# Starts the bot with given token
client.run(secret.bot_token)
