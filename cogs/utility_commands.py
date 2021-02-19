from discord.ext import commands
from discord.ext.commands import Context, MissingRequiredArgument, CheckFailure, CommandInvokeError
from discord import Client, Embed

from fryselBot.system import help, invite, appearance, error_messages, description
from fryselBot.utilities import permission, util


class UtilityCommands(commands.Cog):

    def __init__(self, client: Client, *args, **kwargs):
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
        if isinstance(error, MissingRequiredArgument):
            # Arguments missing
            await error_messages.syntax_error(ctx, description.get_command("prefix"))

        elif isinstance(error, CheckFailure):
            # Missing permissions
            await error_messages.permission_error(ctx, description.get_command("prefix"))

        elif isinstance(error, CommandInvokeError):
            # Invalid prefix
            await error_messages.invalid_input_error(ctx, "Prefix", "The prefix must be a single character")

        else:
            print("Unexpected error while running the prefix command. Error: ", type(error))
            await error_messages.undefined_error(ctx)

        # Delete message
        await util.delete_message(ctx.message)

    @commands.command(name="primary-color", aliases=["primary-colour", "p-color", "p-colour"])
    @commands.check(permission.is_admin)
    async def set_primary_color(self, ctx: Context, primary_color: str):
        """Set primary color command"""
        await appearance.primary_color_command(ctx, primary_color)

    @set_primary_color.error
    async def primary_color_error(self, ctx, error):
        """Handles exceptions while running the primary-color command"""
        if isinstance(error, MissingRequiredArgument):
            # Arguments missing
            await error_messages.syntax_error(ctx, description.get_command("primary-color"))

        elif isinstance(error, CheckFailure):
            # Missing permissions
            await error_messages.permission_error(ctx, description.get_command("primary-color"))

        elif isinstance(error, CommandInvokeError):
            # Invalid hex color
            await error_messages.invalid_input_error(ctx, "Color", "The color must be a HEX color code")

        else:
            print("Unexpected error while running the primary-color command. Error: ", type(error))
            await error_messages.undefined_error(ctx)

        # Delete message
        await util.delete_message(ctx.message)

    @commands.command(name="secondary-color", aliases=["secondary-colour", "s-color", "s-colour"])
    @commands.check(permission.is_admin)
    async def set_secondary_color(self, ctx: Context, secondary_color: str):
        """Set secondary color command"""
        await appearance.secondary_color_command(ctx, secondary_color)

    @set_secondary_color.error
    async def secondary_color_error(self, ctx, error):
        """Handles exceptions while running the secondary-color command"""
        if isinstance(error, MissingRequiredArgument):
            # Arguments missing
            await error_messages.syntax_error(ctx, description.get_command("secondary-color"))

        elif isinstance(error, CheckFailure):
            # Missing permissions
            await error_messages.permission_error(ctx, description.get_command("secondary-color"))

        elif isinstance(error, CommandInvokeError):
            # Invalid hex color
            await error_messages.invalid_input_error(ctx, "Color", "The color must be a HEX color code")

        else:
            print("Unexpected error while running the secondary-color command. Error: ", type(error))
            await error_messages.undefined_error(ctx)

        # Delete message
        await util.delete_message(ctx.message)


def setup(client: Client):
    client.add_cog(UtilityCommands(client))
