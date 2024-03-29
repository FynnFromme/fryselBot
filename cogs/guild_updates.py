from discord.ext import commands
from discord.ext.commands import Bot
from discord import Guild, Role, TextChannel, VoiceChannel, CategoryChannel, Member
from discord.abc import GuildChannel

from system import guilds, welcome, moderation
from database import delete, select
from system.moderation import mute, moderation
from system.private_rooms import private_rooms, settings as pr_settings


class GuildUpdates(commands.Cog):
    """
    Handles changes on the guilds the client is on.
    Attributes:
        client  (Bot): The bot client
    Arguments:
         client (Bot): The bot client
    """
    def __init__(self, client: Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        """Is called when the client joined a new guild"""
        # Add guild to database
        await guilds.join_guild(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        """Is called when the client is removed from a guild"""
        # Remove guild from database
        guilds.remove_guild(guild)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        """Is called when a channel is deleted on a guild"""
        if isinstance(channel, TextChannel):
            guild = channel.guild
            # Welcome System: Check whether the channel is a welcome Channel
            if (channel.id, guild.id) in select.all_welcome_channels():
                # Disable welcome/leave messages on the guild
                welcome.toggle_welcome(guild, disable=True)
                welcome.toggle_leave(guild, disable=True)
                welcome.set_welcome_channel(guild, channel_id=None)

            # Moderation System: Check whether the channel is the moderation log
            if (channel.id, guild.id) in select.all_moderation_logs():
                # Delete mod log out of database
                moderation.set_mod_log(guild, channel_id=None)

            # Private Rooms: Check whether the channel is the settings channel
            if (channel.id, guild.id) in select.all_pr_settings():
                # Disable private rooms on guild
                await private_rooms.disable(guild)

            # Private Rooms: Check whether the channel is a text channel of a private room
            if (channel.id, guild.id) in select.all_pr_text_channels():
                # Delete private room
                private_room = select.PrivateRoom(guild_id=guild.id, text_channel_id=channel.id)
                await private_rooms.delete_private_room(guild, private_room)

        elif isinstance(channel, VoiceChannel):
            guild = channel.guild
            # Private Rooms: Check whether the channel is the cpr channel
            if (channel.id, guild.id) in select.all_cpr_channels():
                # Disable private rooms on guild
                await private_rooms.disable(guild)

            # Private Rooms: Check whether the channel is a private room
            elif (channel.id, guild.id) in select.all_private_rooms():
                # Delete private room
                private_room = select.PrivateRoom(guild_id=guild.id, room_channel_id=channel.id)
                await private_rooms.delete_private_room(guild, private_room)

                # Remove owner permissions
                owner: Member = guild.get_member(private_room.owner_id)
                await private_rooms.remove_owner_permissions(owner, private_room)

            # Private Rooms: Check whether the channel is a move channel
            elif (channel.id, guild.id) in select.all_move_channels():
                # Delete private room
                private_room = select.PrivateRoom(guild_id=guild.id, move_channel_id=channel.id)
                await pr_settings.unlock(guild, private_room)

        elif isinstance(channel, CategoryChannel):
            guild = channel.guild
            # Private Rooms: Check whether the channel is the pr category
            if (channel.id, guild.id) in select.all_pr_categories():
                # Disable private rooms on guild
                await private_rooms.disable(guild)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: GuildChannel):
        """Is called when a channel is created on a guild"""
        if isinstance(channel, TextChannel):
            await mute.setup_mute_in_channel(channel)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: Role):
        """Is called when a role is deleted on a guild"""
        guild = role.guild
        # Check whether the role is in database
        if (role.id, guild.id) in select.all_roles():
            # Delete role out of database
            delete.role(role.id)


def setup(client: Bot):
    client.add_cog(GuildUpdates(client))
