# discord.py imports
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context, Bot
from discord import Guild, Member, Message

# other imports
import os

# fryselBot imports
from fryselBot.system import help, appearance
from fryselBot.utilities import secret
from fryselBot.event_handler import member_handler, guild_handler


async def get_prefix(bot: Bot, message: Message):
    """Returns the prefix for the guild of the message"""
    return appearance.get_prefix(guild_id=message.guild.id)


# Setup intents and create bot client
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None, case_insensitive=True)


# Cog functions
@client.command()
async def load(ctx: Context, extension):
    if ctx.author.id != secret.frysel_id:
        return
    elif extension + ".py" not in os.listdir("./cogs"):
        print("Didn't find cog")
        return
    else:
        client.load_extension(f"cogs.{extension}")
        print("Loaded following cog: ", extension)


@client.command()
async def unload(ctx: Context, extension):
    if ctx.author.id != secret.frysel_id:
        return
    elif extension + ".py" not in os.listdir("./cogs"):
        print("Didn't find cog")
        return
    else:
        client.unload_extension(f"cogs.{extension}")
        print("Unloaded following cog: ", extension)


# Load all cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")


@client.event
async def on_ready():
    """Called when the client is starting"""
    # Set presence of bot
    await client.change_presence(status=discord.Status.online)
    change_status.start()

    # Checks for new / removed guilds after downtime
    guild_handler.check_guilds(client)

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


# TODO: Add cogs for events
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


# Starts the bot with given token
client.run(secret.bot_token)
