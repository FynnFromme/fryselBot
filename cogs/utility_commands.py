from discord.ext import commands
from discord.ext.commands import Context, Bot

from fryselBot.database import manager
from fryselBot.system import help, invite
from fryselBot.utilities import secret


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

    @commands.command(name='test')
    @commands.check(lambda ctx: ctx.author.id == secret.frysel_id)
    async def test(self, ctx: Context):
        """Test command that can onyl be executed by frysel"""
        from fryselBot.system.private_rooms import private_rooms
        await private_rooms.delete_old_channels(ctx.message, ctx.guild)
        await private_rooms.setup_private_rooms(ctx.guild)

        @manager.connection
        def f(_c):
            _c.execute('DELETE FROM private_rooms')
        f()


def setup(client: Bot):
    client.add_cog(UtilityCommands(client))
