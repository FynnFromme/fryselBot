from discord.ext import commands
from discord.ext.commands import Context, Bot

from database import manager
from database.select import PrivateRoom
from system import help, invite
from utilities import secret


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
    async def test(self, ctx: Context, arg: int, arg2=None):
        """Test command that can onyl be executed by frysel"""
        from system.private_rooms import private_rooms, settings

        if arg == 1:
            await private_rooms.delete_old_channels(ctx.message, ctx.guild)
            await private_rooms.setup_private_rooms(ctx.guild)

            @manager.connection
            def f(_c):
                _c.execute('DELETE FROM private_rooms')
            f()
        else:
            private_room = PrivateRoom(ctx.guild.id, ctx.author.id)
            if arg == 2:
                await settings.toggle_hide(ctx.guild, private_room)
            elif arg == 3:
                await settings.toggle_lock(ctx.guild, private_room)
            elif arg == 4 and arg2:
                await settings.set_limit(int(arg2), ctx.guild, private_room)
            elif arg == 5 and arg2:
                await settings.set_name(arg2, ctx.guild, private_room)
            await ctx.message.delete()


def setup(client: Bot):
    client.add_cog(UtilityCommands(client))
