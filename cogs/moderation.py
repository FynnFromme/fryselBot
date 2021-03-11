from discord import Member
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

from fryselBot.utilities import permission, util
from fryselBot.system import moderation as mod, error_messages, description


class Moderation(commands.Cog):
    """
    Handles moderation on guilds
    Attributes:
        client  (Bot): The bot client
    Arguments:
         client (Bot): The bot client
    """

    def __init__(self, client: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.check_expired_bans.start()

    @commands.command(name='clear')
    @commands.check(permission.clear)
    async def clear(self, ctx: Context, amount: int, member: Member = None):
        """Clear command"""
        if member:
            await mod.clear_member(member, ctx.message, amount)
        else:
            await mod.clear(ctx.message, amount)

    @clear.error
    async def clear_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the clear command"""
        await error_messages.error_handler(ctx, error, description.get_command('clear'), 'Amount',
                                           'The amount has to be a positive integer.', True)

    @commands.command(name='kick')
    @commands.check(permission.kick)
    async def kick(self, ctx: Context, member: Member, *, reason: str = None):
        """Kick command"""
        await mod.kick(ctx.message, member, reason)

    @kick.error
    async def kick_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the kick command"""
        if error.args[0].endswith('moderators'):
            # Cannot ban moderators
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot kick moderators.')
        elif error.args[0].endswith('kick the bot'):
            # Cannot ban the bot
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Nice try...')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('kick'), 'Member',
                                               'I am missing permissions to do that.', True)

    @commands.command(name='ban')
    @commands.check(permission.ban)
    async def ban(self, ctx: Context, member: Member, *, reason: str = None):
        """Ban command"""
        await mod.ban(ctx.message, member, reason)

    @ban.error
    async def ban_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the ban command"""
        if error.args[0].endswith('moderators'):
            # Cannot ban moderators
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot ban moderators.')
        elif error.args[0].endswith('ban the bot'):
            # Cannot ban the bot
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Nice try...')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('ban'), 'Member',
                                               'I am missing permissions to do that.', True)

    @commands.command(name='tempban')
    @commands.check(permission.ban)
    async def tempban(self, ctx: Context, member: Member, duration_amount: int, duration_unit: str, *,
                      reason: str = None):
        """Tempban command"""
        await mod.tempban(ctx.message, member, duration_amount, duration_unit, reason)

    @tempban.error
    async def tempban_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the tempban command"""
        if error.args[0].endswith('moderators'):
            # Cannot ban moderators
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot ban moderators.')
        elif error.args[0].endswith('ban the bot'):
            # Cannot ban the bot
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Nice try...')
        elif error.args[0].endswith('Invalid Duration'):
            # Invalid duration
            await error_messages.arguments_error(ctx, description.get_command('tempban'))
        else:
            await error_messages.error_handler(ctx, error, description.get_command('tempban'), 'Member',
                                               'I am missing permissions to do that.', True)

    @commands.command(name='unban')
    @commands.check(permission.ban)
    async def unban(self, ctx: Context, *, user):
        """Unban command"""
        await mod.unban(ctx.message, user)

    @unban.error
    async def unban_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the unban command"""
        if error.args[0].endswith('user is not banned'):
            # User is not banned
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='User',
                                                     description='The user is not banned.')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('unban'), 'User',
                                               'Cannot find the user.', True)

    @tasks.loop(seconds=10)
    async def check_expired_bans(self):
        """Checks for expired temporary bans"""
        await mod.check_tempban_expired(self.client)

    @check_expired_bans.before_loop
    async def before_check_expired_bans(self):
        """Let the check_expired_bans loop begin after the bot is ready"""
        await self.client.wait_until_ready()

    @commands.command(name='warn')
    @commands.check(permission.is_mod)
    async def warn(self, ctx: Context, member: Member, reason: str = None):
        """Warn command"""
        await mod.warn(ctx.message, member, reason)

    @warn.error
    async def warn_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the warn command"""
        if error.args[0].endswith('moderators'):
            # Cannot ban moderators
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot warn moderators.')
        elif error.args[0].endswith('warn the bot'):
            # Cannot ban the bot
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Nice try...')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('warn'), 'Member',
                                               'Cannot find the member.', True)

    @commands.command(name='warns')
    @commands.check(permission.is_mod)
    async def warns(self, ctx: Context, member: Member):
        """Warns command"""
        await mod.warns_of_member(self.client, ctx.message, member)


def setup(client: Bot):
    client.add_cog(Moderation(client))
