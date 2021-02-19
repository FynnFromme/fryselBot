import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context

from fryselBot.system.description import Command
from fryselBot.system import appearance


async def syntax_error(ctx: Context, command: Command) -> None:
    """
    Error message for the case f arguments were missing when calling an command.
    Gives instructions how to call the command.
    :param ctx: Context of error
    :param command: Command that was used
    """
    # Send error message and delete it after some time
    prefix = appearance.get_prefix(ctx.guild.id)
    error_message = await ctx.send(embed=Embed(title="Syntax Error",
                                               description=f"Use `{prefix}{command.syntax}`",
                                               colour=appearance.red_color))
    await error_message.delete(delay=10)


async def permission_error(ctx: Context, command: Command) -> None:
    """
    Error message for the case if arguments were missing when calling an command.
    Gives instructions how to call the command.
    :param ctx: Context of error
    :param command: Command that was used
    """
    # Send error message and delete it after some time
    error_message = await ctx.send(
        embed=Embed(title="Missing Permissions",
                    description=f"You need to have **{command.permissions_required()} "\
                                f"permissions** to use the {command.name} command",
                    colour=appearance.red_color))
    await error_message.delete(delay=10)


async def invalid_input_error(ctx: Context, title: str, description: str) -> None:
    """
    Error message for the case if wrong arguments were given
    :param ctx: Context of error
    :param title: Argument that was invalid
    :param description: Description of error
    """
    # Send error message and delete it after some time
    error_message = await ctx.send(
        embed=Embed(title=f"Invalid {title}",
                    description=description,
                    colour=appearance.red_color))
    await error_message.delete(delay=10)


async def undefined_error(ctx: Context) -> None:
    """
    Error message for undefined errors
    :param ctx: Context of error
    """
    # Send error message and delete it after some time
    error_message = await ctx.send(
        embed=Embed(description="Ooops! Something went wrong :grimacing:",
                    colour=appearance.red_color))
    await error_message.delete(delay=10)
