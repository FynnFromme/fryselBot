from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot

from system import welcome, roles


class Welcome(commands.Cog):
    """
    Handles the welcome system of the bot
    Attributes:
        client  (Bot): The bot client
    Arguments:
         client (Bot): The bot client
    """
    def __init__(self, client: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """Is called when a member joins a guild"""
        if member. bot:
            # Ignore bots
            return

        await welcome.welcome_message(member)
        await welcome.welcome_dm(member)
        await roles.add_auto_roles(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        """Is called when a member leaves a guild"""
        if member. bot:
            # Ignore bots
            return

        await welcome.leave_message(member)


def setup(client: Bot):
    client.add_cog(Welcome(client))
