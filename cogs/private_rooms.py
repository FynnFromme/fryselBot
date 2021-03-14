from discord import Member, VoiceChannel, VoiceState
from discord.ext import commands
from discord.ext.commands import Bot

from fryselBot.system import welcome
from fryselBot.system.private_rooms import private_rooms


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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        """Is called when a member joins a guild"""

        # When member joins a voicechannel
        if before.channel is None and after.channel is not None and before.channel != after.channel:
            channel: VoiceChannel = after.channel

            # Check whether the channel is the cpr channel
            if private_rooms.is_cpr_channel(channel):
                await private_rooms.create_private_room(member)

        # When member leaves a voice_channel
        elif before.channel is not None and after.channel is None and before.channel != after.channel:
            channel: VoiceChannel = before.channel

            # Check whether the channel is a private room
            if private_rooms.is_private_room(channel):

                await private_rooms.leave_private_room(member, channel)

        # When a member moves from one channel to another
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            channel: VoiceChannel = after.channel

            # Check whether the channel is the cpr channel
            if private_rooms.is_cpr_channel(channel):
                await private_rooms.create_private_room(member)

            channel: VoiceChannel = before.channel
            # Check whether the channel is a private room
            if private_rooms.is_private_room(channel):
                await private_rooms.leave_private_room(member, channel)


def setup(client: Bot):
    client.add_cog(PrivateRooms(client))
