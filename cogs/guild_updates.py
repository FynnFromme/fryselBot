from discord.ext import commands
from discord.ext.commands import Context, Bot
from discord import Guild

from fryselBot.system import guilds


class GuildUpdates(commands.Cog):
    """
    Handles changes on the guilds the client is on.
    Attributes:
        client  (Bot): The bot client
    Arguments:
         client (Bot): The bot client
    """
    def __init__(self, client: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        """Is called when the client joined a new guild"""
        # Add guild to database
        guilds.join_guild(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        """Is called when the client is removed from a guild"""
        # Remove guild from database
        guilds.remove_guild(guild)

    # TODO: Add cogs for events (Log various updates regarding bot_channels deleted, guild left/joined. later: roles,
    #  etc.)


def setup(client: Bot):
    client.add_cog(GuildUpdates(client))
