from discord.ext import commands
from discord.ext.commands import Context, Bot
from discord import Message, Guild, TextChannel, Member, Role

from fryselBot.system import description, error_messages, permission
from fryselBot.system.setup import setup as setup_setup, \
    prefix as prefix_setup, \
    color as color_setup, \
    welcome, roles, moderation, private_rooms
from fryselBot.system.private_rooms import private_rooms as pr_sys
from fryselBot.utilities import util


class Setup(commands.Cog):
    """
        Handles the setup commands of the bot
        Attributes:
            client  (Bot): The bot client
        Arguments:
             client (Bot): The bot client
        """

    def __init__(self, client: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Called when there is a reaction on a message added. Handles the ones on setup commands."""
        # Retrieve information out of payload
        guild: Guild = self.client.get_guild(payload.guild_id)
        channel: TextChannel = guild.get_channel(payload.channel_id)
        message: Message = await channel.fetch_message(payload.message_id)
        member: Member = guild.get_member(payload.user_id)
        emoji = payload.emoji.name

        # Ignore messages in the settings channel
        if pr_sys.is_settings_channel(channel):
            return

        await setup_setup.check_reactions(member, guild, channel, message, emoji)

    ######################

    @commands.group(name='setup')
    @commands.check(permission.is_admin)
    async def setup(self, ctx: Context):
        """Group of setup commands."""
        # Send setup page if the setup command is called without subcommand
        if ctx.invoked_subcommand is None:
            await setup_setup.setup_page(ctx.channel, ctx.guild)

    @setup.error
    async def setup_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the setup command"""
        await error_messages.error_handler(ctx, error, description.get_command('setup'), 'Setup',
                                           '', True)

    ######################

    @setup.command(name='prefix')
    async def prefix(self, ctx: Context, prefix: str = None):
        """Set prefix command"""
        if prefix:
            # Set prefix if prefix is given
            await prefix_setup.setup_prefix(ctx.channel, ctx.guild, ctx.message, prefix)
        else:
            # Send prefix page if no prefix is given
            await prefix_setup.prefix_page(ctx.channel, ctx.guild)

    @prefix.error
    async def prefix_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the prefix command"""
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command('prefix'), 'Prefix',
                                           'The prefix must be a single character.', True)

    #####################

    @setup.command(name='color', aliases=['colour'])
    async def color(self, ctx: Context, color: str = None):
        """Set color command"""
        if color:
            # Set color if color is given
            await color_setup.setup_color(ctx.channel, ctx.guild, ctx.message, color)
        else:
            # Send color page if no color is given
            await color_setup.color_page(ctx.channel, ctx.guild)

    @color.error
    async def color_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the color command"""
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command('color'), 'Color',
                                           'The color must be a HEX color code.', True)

    #####################

    @setup.group(name='welcome')
    async def welcome(self, ctx: Context):
        """Setup welcome system command"""
        if ctx.invoked_subcommand is None:
            # Send welcome page if no args are given
            await welcome.welcome_page(ctx.channel, ctx.guild)

    @welcome.error
    async def welcome_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the welcome command"""
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command('welcome'), 'Welcome', '', True)

    @welcome.command(name='channel')
    async def welcome_channel(self, ctx: Context, welcome_channel: TextChannel):
        """Command for setting the welcome channel"""
        await welcome.setup_welcome_channel(ctx.channel, ctx.guild, ctx.message, welcome_channel)

    @welcome_channel.error
    async def welcome_channel_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the welcome channel command"""
        # Handle the error messages
        await error_messages.error_handler(ctx, error, description.get_command('welcome channel'),
                                           'Welcome Channel', 'Cannot find the channel.', True)

    @welcome.command(name='dm')
    async def welcome_dm_text(self, ctx: Context, *, text: str):
        """Command for setting the text for welcome dms"""
        await welcome.setup_welcome_dm_text(ctx.channel, ctx.guild, ctx.message, text)

    @welcome_dm_text.error
    async def welcome_dm_text_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the welcome channel command"""
        # Handle error messages
        await error_messages.error_handler(ctx, error, description.get_command('welcome dm'),
                                           'Welcome DM text', 'Give a text that will be send to new members via DM.')

    ###########################

    @setup.group(name='roles')
    async def roles(self, ctx: Context):
        """Setup roles command"""
        if ctx.invoked_subcommand is None:
            # Send welcome page if no args are given
            await roles.roles_page(ctx.channel, ctx.guild)

    @roles.error
    async def roles_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the roles command"""
        # Handles the error messages
        await error_messages.error_handler(ctx, error, description.get_command('roles'), 'Roles', '', True)

    @roles.command(name='add')
    async def roles_add(self, ctx: Context, type_: str, role: Role):
        """Command for adding roles"""
        await roles.add_role(ctx.guild, role, type_, ctx.channel, ctx.message)

    @roles_add.error
    async def roles_add_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the roles add command"""
        # Handle error messages
        if error.args[0].endswith('add default role'):
            # Cannot add default role
            await util.delete_message(ctx.message)
            await error_messages.invalid_input_error(ctx, title='Role',
                                                     description='Cannot add @everyone')
        else:
            await error_messages.error_handler(ctx, error, description.get_command('roles add'), 'Type',
                                               'The type must be either *admin*, *moderator* or *autorole*.', True)

    @roles.command(name='remove')
    async def roles_remove(self, ctx: Context, type_: str, role: Role):
        """Command for removing roles"""
        await roles.remove_role(ctx.guild, role, type_, ctx.channel, ctx.message)

    @roles_remove.error
    async def roles_remove_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the roles remove command"""
        # Handle error messages
        await error_messages.error_handler(ctx, error, description.get_command('roles remove'), 'Type',
                                           'The type must be either *admin*, *moderator* or *supporter*.', True)

    ########################

    @setup.group(name='moderation')
    async def moderation(self, ctx: Context):
        """Setup moderation command"""
        if ctx.invoked_subcommand is None:
            # Send welcome page if no args are given
            await moderation.moderation_page(ctx.channel, ctx.guild)

    @moderation.error
    async def moderation_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the moderation command"""
        # Handle the error messages
        await error_messages.error_handler(ctx, error, description.get_command('moderation'), 'Moderation', '', True)

    @moderation.command(name='log')
    async def set_mod_log(self, ctx: Context, mod_log: TextChannel):
        """Command to set the moderation log"""
        await moderation.setup_moderation_log(ctx.channel, ctx.guild, ctx.message, mod_log)

    @set_mod_log.error
    async def mod_log_error(self, ctx: Context, error: Exception):
        """Handles exceptions while running the moderation log command"""
        # Handle error messages
        await error_messages.error_handler(ctx, error, description.get_command('moderation log'), 'Channel',
                                           'Cannot find the channel.', True)

    ####################################

    @setup.group(name='private')
    async def private(self, ctx: Context):
        """Private group: Only for private rooms command"""
        if ctx.invoked_subcommand is None:
            # Send error message
            await error_messages.arguments_error(ctx, description.get_command('private rooms'))

    @private.command(name='rooms')
    async def private_rooms(self, ctx: Context):
        """Setup private rooms command"""
        await private_rooms.private_rooms_page(ctx.channel, ctx.guild)

    @private_rooms.error
    async def pr_error(self, ctx: Context, error: Exception):
        await error_messages.error_handler(ctx, error, description.get_command('private rooms'), '', '', True)
        

def setup(client: Bot):
    client.add_cog(Setup(client))
