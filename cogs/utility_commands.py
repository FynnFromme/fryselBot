from discord.ext import commands
from discord.ext.commands import Context, Bot

from fryselBot.system import help, invite


class UtilityCommands(commands.Cog):
    """
        Handles the utility commands of the bot
        Attributes:
            client  (Bot): The bot client
        Arguments:
             client (Bot): The bot client
        """

    def __init__(self, client: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @commands.command(name='help')
    async def _help(self, ctx: Context, *, command: str = None):
        """Help command"""
        if command:
            await help.cmd_help(ctx.message, command)
        else:
            await help.help_command(ctx.message)

    @commands.command(name='invite')
    async def invite(self, ctx: Context):
        """Invite command"""
        await invite.invite_command(ctx.message)


def setup(client: Bot):
    client.add_cog(UtilityCommands(client))
