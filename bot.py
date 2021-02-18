# discord.py imports
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context, Bot
from discord import Guild, Member, Message

# other imports
import asyncio
from itertools import cycle

# fryselBot imports
from fryselBot.utilities import style, secret
from fryselBot.event_handler import message_handler, guild_handler, member_handler
from fryselBot import commands as cmd


async def get_prefix(bot: Bot, message: Message):
    """Returns the prefix for the guild of the message"""
    return style.get_prefix(guild_id=message.guild.id)


# Setup intents and create bot client
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online)
    change_status.start()
    print("{} is logged in as user {}".format(style.bot_name, client.user.name))  # States, that the bot is ready
    guild_handler.check_guilds(client)  # Checks for new / removed guilds after downtime


# List of status for the bot
status = cycle(["Hey there!", f"v. {style.version} | {style.default_prefix}help"])


@tasks.loop(seconds=30)
async def change_status():
    """Set the status of bot. Cycles through multiple status over time."""
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_message(message: Message):
    """Is called when there is a new message in a text channel."""
    if message.author.bot:
        return
    await message_handler.new_message(message)
    await client.process_commands(message)


@client.event
async def on_guild_join(guild: Guild):
    """Is called when the client joined a new guild"""
    guild_handler.join_guild(guild)


@client.event
async def on_guild_remove(guild: Guild):
    """Is called when the client is removed from a guild"""
    guild_handler.remove_guild(guild)


@client.event
async def on_member_join(member: Member):
    """Is called when a member joins a guild"""
    await member_handler.member_joined(member)


@client.event
async def on_member_remove(member: Member):
    """Is called when a member leaves a guild"""
    await member_handler.member_left(member)


@client.command(aliases=["help"])
async def _help(cxt):
    await cmd.help.response(cxt.message)


# Starts the bot with given token
client.run(secret.bot_token)
