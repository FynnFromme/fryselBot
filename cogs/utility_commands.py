from discord.ext import commands
from discord.ext.commands import Context, Bot

from fryselBot.system import help, invite, appearance, error_messages, description
from fryselBot.utilities import permission


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

    @commands.command(name="help")
    async def _help(self, ctx: Context):
        """Help command"""
        await help.help_command(ctx.message)

    @commands.command()
    async def invite(self, ctx: Context):
        """Invite command"""
        await invite.invite_command(ctx.message)

    @commands.command(name="prefix")
    @commands.check(permission.is_admin)
    async def set_prefix(self, ctx: Context, prefix: str):
        """Set prefix command"""
        await appearance.prefix_command(ctx, prefix)

    @set_prefix.error
    async def prefix_error(self, ctx, error):
        """Handles exceptions while running the prefix command"""
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command("prefix"), "Prefix",
                                           "The prefix must be a single character or 'default'", True)

    @commands.command(name="primary-color", aliases=["primary-colour", "p-color", "p-colour"])
    @commands.check(permission.is_admin)
    async def set_primary_color(self, ctx: Context, primary_color: str):
        """Set primary color command"""
        await appearance.primary_color_command(ctx, primary_color)

    @set_primary_color.error
    async def primary_color_error(self, ctx, error):
        """Handles exceptions while running the primary-color command"""
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command("primary-color"), "Color",
                                           "The color must be a HEX color code or 'default'", True)

    @commands.command(name="secondary-color", aliases=["secondary-colour", "s-color", "s-colour"])
    @commands.check(permission.is_admin)
    async def set_secondary_color(self, ctx: Context, secondary_color: str):
        """Set secondary color command"""
        await appearance.secondary_color_command(ctx, secondary_color)

    @set_secondary_color.error
    async def secondary_color_error(self, ctx, error):
        """Handles exceptions while running the secondary-color command"""
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command("secondary-color"), "Color",
                                           "The color must be a HEX color code or 'default'", True)

    # TODO: Add setup command for mod, admin roles


def setup(client: Bot):
    client.add_cog(UtilityCommands(client))
