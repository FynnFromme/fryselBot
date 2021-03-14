from datetime import datetime, timedelta
from typing import Union

from discord import Member, Role
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

from fryselBot.database import delete, select
from fryselBot.utilities import util
from fryselBot.system import description, error_messages, permission
from fryselBot.system.moderation import moderation as mod, clear, kick, ban, mute, warn, report


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

        # Start loops
        self.check_old_warns.start()
        self.check_expired.start()

    @commands.command(name='clear')
    @commands.check(permission.clear)
    async def clear(self, ctx: Context, amount: int = 100, member: Member = None):
        """Clear command"""
        if member:
            await clear.clear_member(member, ctx.message, amount)
        else:
            await clear.clear_messages(ctx.message, amount)

    @clear.error
    async def clear_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the clear command"""
        await error_messages.error_handler(ctx, error, description.get_command('clear'), 'Amount',
                                           'The amount has to be a positive integer.', True)

    @commands.command(name='kick')
    @commands.check(permission.kick)
    async def kick(self, ctx: Context, member: Member, *, reason: str = None):
        """Kick command"""
        await kick.kick_cmd(ctx.message, member, self.client, reason)

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

    @commands.command(name='ban', aliases=['bigmac'])
    @commands.check(permission.ban)
    async def ban(self, ctx: Context, member: Member, *, reason: str = None):
        """Ban command"""
        await ban.ban_cmd(ctx.message, member, self.client, reason)

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
    async def tempban(self, ctx: Context, member: Member, duration_amount: Union[float, int], duration_unit: str, *,
                      reason: str = None):
        """Tempban command"""
        await ban.tempban_cmd(ctx.message, member, duration_amount, duration_unit, self.client, reason)

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
        await ban.unban_cmd(ctx.message, user)

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

    @commands.command(name='mute')
    @commands.check(permission.mute)
    async def mute(self, ctx: Context, member: Member, *, reason: str = None):
        """Mute command"""
        await mute.mute_cmd(ctx.message, member, reason)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """Called when a member joines a guild"""
        # Check whether the member is muted
        if mute.is_muted(member):
            mute_role: Role = await mute.get_mute_role(member.guild)
            await member.add_roles(mute_role, reason='Member was muted when joining the server.')

    @mute.error
    async def mute_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the mute command"""
        if error.args[0].endswith('moderators'):
            # Cannot mute moderators
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot mute moderators.')
        elif error.args[0].endswith('mute the bot'):
            # Cannot mute the bot
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Nice try...')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('mute'), 'Member',
                                               'Cannot find the member.', True)

    @commands.command(name='tempmute')
    @commands.check(permission.mute)
    async def tempmute(self, ctx: Context, member: Member, duration_amount: Union[float, int], duration_unit: str, *,
                       reason: str = None):
        """tempmute command"""
        await mute.tempmute_cmd(ctx.message, member, duration_amount, duration_unit, reason)

    @tempmute.error
    async def tempmute_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the tempmute command"""
        if error.args[0].endswith('moderators'):
            # Cannot mute moderators
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot ban moderators.')
        elif error.args[0].endswith('mute the bot'):
            # Cannot mute the bot
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Nice try...')
        elif error.args[0].endswith('Invalid Duration'):
            # Invalid duration
            await error_messages.arguments_error(ctx, description.get_command('tempmute'))
        else:
            await error_messages.error_handler(ctx, error, description.get_command('tempmute'), 'Member',
                                               'Cannot find the member.', True)

    @tasks.loop(seconds=10)
    async def check_expired(self):
        """Checks for expired temporary mutes"""
        await mute.check_expired(self.client)
        await ban.check_expired(self.client)

    @check_expired.before_loop
    async def before_check_expired(self):
        """Wait until bot is ready"""
        await self.client.wait_until_ready()

    @commands.command(name='unmute')
    @commands.check(permission.ban)
    async def unmute(self, ctx: Context, member: Member):
        """Unmute command"""
        await mute.unmute_cmd(ctx.message, member)

    @unmute.error
    async def unmute_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the unmute command"""
        if error.args[0].endswith('is not muted'):
            # Member is not muted
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='The member is not muted.')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('unmute'), 'Member',
                                               'Cannot find the member.', True)

    @commands.command(name='warn')
    @commands.check(permission.is_mod)
    async def warn(self, ctx: Context, member: Member, *, reason: str = None):
        """Warn command"""
        await warn.warn_cmd(ctx.message, member, reason)

    @warn.error
    async def warn_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the warn command"""
        if error.args[0].endswith('moderators'):
            # Cannot warn moderators
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot warn moderators.')
        elif error.args[0].endswith('warn the bot'):
            # Cannot warn the bot
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
        await warn.warns_of_member_cmd(self.client, ctx.message, member)

    @warns.error
    async def warns_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the warns command"""
        await error_messages.error_handler(ctx, error, description.get_command('warns'), 'Member',
                                           'Cannot find the member.', True)

    @tasks.loop(hours=24)
    async def check_old_warns(self):
        """Checks for old warns"""
        # Get date of 1 year ago
        date = datetime.utcnow() - timedelta(days=365)
        for w in select.warns_date(date=date, after=False):
            delete.warn(w.warn_id)

    @commands.command(name='report')
    async def report(self, ctx: Context, member: Member, *, reason: str):
        """Report command"""
        await report.report_cmd(ctx.message, member, reason)

    @report.error
    async def report_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the repor command"""
        if not mod.get_mod_log(ctx.guild):
            # Ignore if the log is not set up
            return
        elif error.args[0].endswith('moderators'):
            # Cannot report moderators
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot report moderators.')
        elif error.args[0].endswith('report the bot'):
            # Cannot report the bot
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Nice try...')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('report'), 'Member',
                                               'Cannot find the member.', True)

    @commands.command(name='reports')
    @commands.check(permission.is_mod)
    async def reports(self, ctx: Context, member: Member):
        """Reports command"""
        await report.reports_of_member_cmd(self.client, ctx.message, member)

    @reports.error
    async def reports_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the reports command"""
        if not mod.get_mod_log(ctx.guild):
            # Ignore if the log is not set up
            return
        await error_messages.error_handler(ctx, error, description.get_command('reports'), 'Member',
                                           'Cannot find the member.', True)


def setup(client: Bot):
    client.add_cog(Moderation(client))
