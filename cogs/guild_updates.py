from discord.ext import commands
from discord.ext.commands import Bot
from discord import Guild, Role
from discord.abc import GuildChannel

from fryselBot.system import guilds, welcome
from fryselBot.database import select, delete


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

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        """Is called when a channel is deleted on a guild"""
        guild = channel.guild
        # Welcome System: Check whether the channel is a welcome Channel
        if (channel.id, guild.id) in select.all_welcome_channels():
            # Disable welcome/leave messages on the guild
            welcome.toggle_welcome(guild, disable=True)
            welcome.toggle_leave(guild, disable=True)
            welcome.set_welcome_channel(guild, channel_id=None)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: Role):
        """Is called when a role is deleted on a guild"""
        guild = role.guild
        # Check whether the role is in database
        if (role.id, guild.id) in select.all_roles():
            # Delete role out of database
            delete.role(role.id)

    # TODO: Add cogs for events (Log various updates regarding bot_channels deleted, guild left/joined. later: roles,
    #  etc.)


def setup(client: Bot):
    client.add_cog(GuildUpdates(client))
