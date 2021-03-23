from discord import Member, VoiceChannel, VoiceState, Guild, TextChannel, Message, NotFound
from discord.ext import commands, tasks
from discord.ext.commands import Bot

from fryselBot.database.manager import DatabaseEntryError
from fryselBot.database.select import PrivateRoom
from fryselBot.system import welcome, waiting_for_responses
from fryselBot.system.private_rooms import private_rooms, settings
from fryselBot.utilities import secret


class PrivateRooms(commands.Cog):
    """
    Handles the welcome system of the bot
    Attributes:
        client  (Bot): The bot client
    Arguments:
         client (Bot): The bot client
    """
    def __init__(self, client: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.check_activity.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        """Is called when a member joins a guild"""

        # When member joins a voicechannel
        if before.channel is None and after.channel is not None and before.channel != after.channel:
            channel: VoiceChannel = after.channel
            # Check whether the channel is the cpr channel
            if private_rooms.is_cpr_channel(channel):
                await private_rooms.create_private_room(member)
            # Check whether the channel is the cpr channel
            if private_rooms.is_private_room(channel):
                await private_rooms.join_private_room(member, channel)

        # When member leaves a voice_channel
        elif before.channel is not None and after.channel is None and before.channel != after.channel:
            channel: VoiceChannel = before.channel
            # Check whether the channel is a private room
            if private_rooms.is_private_room(channel):
                await private_rooms.leave_private_room(member, channel)

        # When a member moves from one channel to another
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            channel: VoiceChannel = after.channel

            # Check whether joined a cpr channel
            if private_rooms.is_cpr_channel(channel):
                await private_rooms.create_private_room(member)

            # Check whether joined a private room
            if private_rooms.is_private_room(channel):
                await private_rooms.join_private_room(member, channel)

            channel: VoiceChannel = before.channel
            # Check whether the channel is a private room
            if private_rooms.is_private_room(channel):
                await private_rooms.leave_private_room(member, channel)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Called when there is a reaction on a message added. Handles the ones on setup commands."""
        # Retrieve information out of payload
        try:
            guild: Guild = self.client.get_guild(payload.guild_id)
            channel: TextChannel = guild.get_channel(payload.channel_id)
            message: Message = await channel.fetch_message(payload.message_id)
            member: Member = guild.get_member(payload.user_id)
            emoji = payload.emoji.name
        except NotFound:
            pass

        # Check reaction if the reaction is in a settings channel and the member owns a private room
        if private_rooms.is_settings_channel(channel):
            try:
                private_room: PrivateRoom = PrivateRoom(guild.id, owner_id=member.id)
            except DatabaseEntryError:
                if member.id != secret.bot_id:
                    await message.remove_reaction(emoji, member)
                return
            else:
                await settings.check_reactions(member, guild, private_room, message, emoji, True)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """..."""
        if isinstance(message.channel, TextChannel):
            if private_rooms.is_settings_channel(message.channel) and message.author.id != secret.bot_id:
                waiting_for_responses.handle_response(message)
                await message.delete()

    #####################

    @tasks.loop(minutes=1)
    async def check_activity(self):
        """Checks for new activities"""
        await settings.handle_game_activity(self.client)

    @check_activity.before_loop
    async def before_check_activity(self):
        """Wait until bot is ready"""
        await self.client.wait_until_ready()

    #####################


def setup(client: Bot):
    client.add_cog(PrivateRooms(client))
