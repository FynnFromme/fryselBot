import discord
import asyncio

from discord.message import Message
from discord import Guild, Member

from fryselBot.utilities import style, secret
from event_handler import message_handler, guild_handler, member_handler

# Setup intents and create client
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

# Use from discord.ext import commands

@client.event
async def on_ready():
    print("{} is logged in as user {}".format(style.bot_name, client.user.name))  # States, that the bot is ready
    client.loop.create_task(status_task())  # Sets the status of the bot
    guild_handler.check_guilds(client)  # Checks for new / removed guilds after downtime


async def status_task():
    """Set the status of bot. Cycles through multiple status over time."""
    # Cycles through different status over time
    await client.change_presence(status=discord.Status.online)
    while True:
        await client.change_presence(activity=discord.Game("v. {} | {}help".format(style.version,
                                                                                   style.default_prefix)))
        await asyncio.sleep(60)
        await client.change_presence(activity=discord.Game("Hey there!"))
        await asyncio.sleep(60)


@client.event
async def on_message(message: Message):
    """Is called when there is a new message in a text channel."""
    await message_handler.new_message(message)


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
