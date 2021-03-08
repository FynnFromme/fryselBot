from discord import Embed
from discord.ext.commands import Context, MissingRequiredArgument, CommandInvokeError, CheckFailure

from fryselBot.system.description import Command
from fryselBot.system import appearance
from fryselBot.utilities import util


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


async def error_handler(ctx: Context, error: Exception, command: Command,
                        invalid_arg_title: str, invalid_arg_desc: str, delete_message: bool = False) -> None:
    """
    Handles following command errors:
    - MissingRequiredArgument
    - CheckFailure (interpreted as permission missing)
    - CommandInvokeError (interpreted as invalid input)
    :param ctx: Error context
    :param error: Error object
    :param command: Command which led to the error
    :param invalid_arg_title: Title for invalid input message
    :param invalid_arg_desc: Description for invalid input message
    :param delete_message: Whether the message of the user should be deleted
    """
    if isinstance(error, MissingRequiredArgument):
        # Arguments missing
        await syntax_error(ctx, command)

    elif isinstance(error, CheckFailure):
        # Missing permissions
        await permission_error(ctx, command)

    elif isinstance(error, CommandInvokeError):
        # Invalid arguments
        await invalid_input_error(ctx, invalid_arg_title, invalid_arg_desc)

    else:
        # Other errors
        print(f"Unexpected error while running the {command.name} command. Error: {type(error)}")
        await undefined_error(ctx)

    # Delete message
    if delete_message:
        await util.delete_message(ctx.message)