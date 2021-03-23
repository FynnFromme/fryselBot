import os

from discord.ext.commands import Context, Bot, ExtensionAlreadyLoaded, ExtensionNotLoaded
from discord import Embed
from utilities import util
from system import appearance


async def load_command(ctx: Context, extension: str, client: Bot) -> None:
    """
    Command to load an extension.
    :param ctx: Command context
    :param extension: Extension to be loaded
    :param client: Bot client
    """
    # Delete message
    await ctx.message.delete()

    if extension == 'cogs':
        # Don't load the cogs extension
        raise util.InvalidInputError('Cannot unload cogs extension')

    elif extension + '.py' not in os.listdir('./cogs/'):
        # Extension doesn't exist
        raise util.InvalidInputError("Didn't find the cog to load")

    else:
        try:
            client.load_extension(f'cogs.{extension}')
        except ExtensionAlreadyLoaded:
            # Ignore if the extension was already loaded
            pass

        msg = await ctx.send(embed=Embed(title='Extension Loaded', description=extension,
                                         color=appearance.success_color))
        await msg.delete(delay=10)


async def unload_command(ctx: Context, extension: str, client: Bot) -> None:
    """
    Command to unload an extension.
    :param ctx: Command context
    :param extension: Extension to be unloaded
    :param client: Bot client
    """
    # Delete message
    await ctx.message.delete()

    if extension == 'cogs':
        # Don't unload the cogs extension
        raise util.InvalidInputError('Cannot unload cogs extension')

    elif extension + '.py' not in os.listdir('./cogs/'):
        # Extension doesn't exist
        raise util.InvalidInputError("Didn't find the cog to unload")

    else:
        try:
            client.unload_extension(f'cogs.{extension}')
        except ExtensionNotLoaded:
            # Ignore if the extension was already unloaded
            pass

        msg = await ctx.send(embed=Embed(title='Extension Unloaded', description=extension,
                                         color=appearance.success_color))
        await msg.delete(delay=10)


def load_all(client: Bot) -> None:
    """
    Load all extensions of the client
    :param client: Client to load extensions
    """
    # Load all extensions
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
