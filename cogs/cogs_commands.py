from discord.ext import commands
from discord.ext.commands import Context, Bot, CheckFailure

from fryselBot.system import cogs, description, error_messages
from fryselBot.utilities import secret


class Cogs(commands.Cog):
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

    @commands.command(name='load')
    @commands.check(lambda ctx: ctx.author.id == secret.frysel_id)
    async def load(self, ctx: Context, extension: str):
        """Load command"""
        # Load the extension
        await cogs.load_command(ctx, extension, self.client)

    @load.error
    async def load_error(self, ctx, error):
        """Handles exceptions while running the load command"""
        # No Permission error
        if isinstance(error, CheckFailure):
            return
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command('load'), 'Extension',
                                           "Didn't find the extension", True)

    @commands.command(name='unload')
    @commands.check(lambda ctx: ctx.author.id == secret.frysel_id)
    async def unload(self, ctx: Context, extension: str):
        """Unload command"""
        # Load the extension
        await cogs.unload_command(ctx, extension, self.client)

    @unload.error
    async def unload_error(self, ctx, error):
        """Handles exceptions while running the unload command"""
        # No Permission error
        if isinstance(error, CheckFailure):
            return
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command('unload'), 'Extension',
                                           "Didn't find the extension", True)


def setup(client: Bot):
    client.add_cog(Cogs(client))
