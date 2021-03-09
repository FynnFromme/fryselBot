from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot, Context, MemberNotFound

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

    @commands.command(name='clear')
    @commands.check(permission.clear)
    async def clear(self, ctx: Context, amount: int, member: Member = None):
        """Clear command"""
        if member:
            await mod.clear_member(member, ctx.channel, amount)
        else:
            await mod.clear(ctx.channel, amount)

    @clear.error
    async def clear_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the clear command"""
        if isinstance(error, MemberNotFound):
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Member',
                                                     description='Cannot find the member.')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('clear'), 'Amount',
                                               'The amount has to be a positive integer.', True)

    @commands.command(name='kick')
    @commands.check(permission.kick)
    async def kick(self, ctx: Context, member: Member, *, reason: str = None):
        """Kick command"""
        await mod.kick(ctx.guild, ctx.channel, member, reason)

def setup(client: Bot):
    client.add_cog(Moderation(client))
