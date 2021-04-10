import asyncio
from datetime import datetime

from discord import VoiceChannel, Guild, Role, PermissionOverwrite, CategoryChannel, Member, NotFound, TextChannel, \
    Embed, Message, Forbidden, Client, Game

from database import update, select
from database.manager import DatabaseEntryError
from database.select import PrivateRoom
from system import appearance, waiting_for_responses
from system.private_rooms import private_rooms
from utilities import secret

# The default name of private rooms
default_name = f"<owner>'s Room"


def get_name(owner: Member) -> str:
    """
    Get the name for the private rooms of the owner
    :param owner: Owner of the private room
    :return: Name for the private room
    """
    guild = owner.guild
    default_guild_name = select.default_pr_name(guild.id)

    # Check for a default name for the guild
    if default_guild_name:
        name = default_guild_name.replace('<owner>', owner.display_name)
    else:
        name = default_name.replace('<owner>', owner.display_name)
    return name


async def set_name(name: str, guild: Guild, private_room: PrivateRoom) -> None:
    """
    Set the name for the private room
    :param name: New name of the private room
    :param guild: Guild of private room
    :param private_room: Private room to change name
    """
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    text_channel: TextChannel = guild.get_channel(private_room.text_channel_id)
    owner: Member = guild.get_member(private_room.owner_id)

    name.replace('<owner>', owner.mention)

    if not pr_channel:
        # Ignore if channel does not exist anymore
        return

    if pr_channel.name == name:
        # Ignore if the name has not changed
        return

    # Try to change the names of the room and channel
    try:
        await pr_channel.edit(name=name)
    except NotFound:
        pass

    if text_channel:
        try:
            await text_channel.edit(name=name)
        except NotFound:
            pass


async def name_response(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Handle setting a new name by waiting for a response in the settings channel
    :param guild: Guild of private room
    :param private_room: Private room to handle setting the new name
    """
    owner: Member = guild.get_member(private_room.owner_id)
    settings_channel: TextChannel = private_rooms.get_settings_channel(guild)

    response = await waiting_for_responses.wait_for_response(owner, settings_channel, 10, True)

    if not response:
        return

    if len(response) > 20:
        return

    pr_channel = guild.get_channel(private_room.room_channel_id)

    if not(pr_channel.name.startswith('Playing') and private_room.game_activity):
        await set_name(response, guild, private_room)

    update.pr_name(private_room.room_id, response)


async def handle_game_activity(client: Client) -> None:
    """
    Refresh game activity for all active private rooms
    :param client: Bot client
    """
    # Get all active private rooms
    rooms: list[PrivateRoom] = [PrivateRoom(guild_id=g_id, room_channel_id=pr_id)
                                for pr_id, g_id
                                in select.all_private_rooms()]
    for room in rooms:
        guild: Guild = client.get_guild(room.guild_id)
        if room.game_activity:
            # Refresh game activity
            await check_game_activity(guild, room)
        else:
            # Set the name of the private room without game activity
            if room.name:  # If there is a custom name for the private room
                await set_name(room.name, guild, room)
            else:
                owner = guild.get_member(room.owner_id)
                name = get_name(owner)
                await set_name(name, guild, room)


async def check_game_activity(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Check the main game activity of the private room and refresh the name
    :param guild: Guild of private room
    :param private_room: Private room to check game activity
    """
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    owner: Member = guild.get_member(private_room.owner_id)

    # Create dict of games and how many members play them
    games: dict[Game, float] = {}
    for member in pr_channel.members:
        for game in filter(lambda a: isinstance(a, Game), member.activities):
            # Owner activities are more important
            if owner.id == member.id:
                if game in games:
                    games[game] += 1.5
                else:
                    games[game] = 1.5
            else:
                if game in games:
                    games[game] += 1.5
                else:
                    games[game] = 1.5

    if games:
        game: Game = max(games, key=games.get)
        await set_name(f'Playing {game.name}', guild, private_room)
    else:
        if private_room.name:
            await set_name(private_room.name, guild, private_room)
        else:
            name = get_name(owner)
            await set_name(name, guild, private_room)


async def toggle_game_activity(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Toggle that game activity is shown in the name of the private room
    :param guild: Guild of private room
    :param private_room: Private room to toggle game activit
    """
    if private_room.game_activity:
        # Disable game activity
        update.pr_game_activity(argument=private_room.room_id, value=False)
        owner: Member = guild.get_member(private_room.owner_id)
        if private_room.name:
            await set_name(private_room.name, guild, private_room)
        else:
            name = get_name(owner)
            await set_name(name, guild, private_room)
    else:
        # Enable game activity
        update.pr_game_activity(argument=private_room.room_id, value=True)


async def lock(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Lock the private room
    :param guild: Guild of private room
    :param private_room: Privte room to lock
    """
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    default_role: Role = guild.default_role

    # Fetch category and owner
    pr_category: CategoryChannel = guild.get_channel(
        select.pr_categroy_id(guild.id))
    pr_owner: Member = guild.get_member(private_room.owner_id)

    await asyncio.sleep(0.2)
    try:
        PrivateRoom(guild_id=guild.id, room_channel_id=pr_channel.id)
    except DatabaseEntryError:
        return

    # Set permission in pr_channel
    overwrite: PermissionOverwrite = pr_channel.overwrites_for(default_role)
    overwrite.update(connect=False)
    await pr_channel.set_permissions(default_role, overwrite=overwrite)

    # Create move channel and set perms
    perms = {pr_owner: PermissionOverwrite(connect=False, move_members=True),
             default_role: PermissionOverwrite(speak=False)}

    if private_room.hidden:
        perms[default_role] = PermissionOverwrite(view_channel=False)

    move_channel: VoiceChannel = await guild.create_voice_channel(f'↑ Waiting for move ↑', category=pr_category,
                                                                  overwrites=perms,
                                                                  reason='Locked private room')
    await move_channel.edit(position=pr_channel.position + 1)

    # Update database
    update.pr_locked(private_room.room_id, value=True)
    update.pr_move_channel_id(private_room.room_id, value=move_channel.id)


async def unlock(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Unlock the private room
    :param guild: Guild of private room
    :param private_room: Private room to unlock
    """
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    default_role: Role = guild.default_role

    if not private_room.locked:  
        # Ignore if the private room is already unlocked
        return
    
    # Set permission in pr_channel
    if pr_channel:
        overwrite: PermissionOverwrite = pr_channel.overwrites_for(
            default_role)
        overwrite.update(connect=True)
        try:
            await pr_channel.set_permissions(default_role, overwrite=overwrite)
        except NotFound:
            pass

    # Remove move channel
    move_channel: VoiceChannel = guild.get_channel(
        private_room.move_channel_id)
    if move_channel:
        await move_channel.delete(reason='Unlocked private room')

    # Update database
    update.pr_locked(private_room.room_id, value=False)
    update.pr_move_channel_id(private_room.room_id, value=None)


async def toggle_privacy(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Toggle privacy of private room
    :param guild: Guild of private room
    :param private_room: Private room to toggle privacy
    """
    if private_room.locked:
        # Unlock room
        await unlock(guild, private_room)
    else:
        # Lock room
        await lock(guild, private_room)


async def set_user_limit(limit: int, guild: Guild, private_room: PrivateRoom) -> None:
    """
    Set the user limit of a private room
    :param limit: New limit of the private room
    :param guild: Guild of private room
    :param private_room: Private room to set user limit
    """
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)

    if not pr_channel:
        # Ignore if the channel doesn't exist
        return
    
    if pr_channel.user_limit != limit:
        await pr_channel.edit(user_limit=limit)

    # Update database
    update.pr_user_limit(private_room.room_id, limit)


async def limit_response(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Handle setting a new user limit by waiting for a response in the settings channel
    :param guild: Guild of private room
    :param private_room: Private room to handle setting the new user limit
    """
    owner: Member = guild.get_member(private_room.owner_id)
    settings_channel: TextChannel = private_rooms.get_settings_channel(guild)

    response = await waiting_for_responses.wait_for_response(owner, settings_channel, 10, True)

    if not response:
        return

    if not response.isnumeric():
        return

    limit = int(response)

    if limit > 99:
        limit = 99
    elif limit < 0:
        limit = 0

    await set_user_limit(limit, guild, private_room)


async def hide(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Hide the private room
    :param guild: Guild of private room
    :param private_room: Private room to hide
    """
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    default_role: Role = guild.default_role

    # Set permission in pr_channel
    overwrite: PermissionOverwrite = pr_channel.overwrites_for(default_role)
    overwrite.update(view_channel=False)
    await pr_channel.set_permissions(default_role, overwrite=overwrite)

    if private_room.locked:
        move_channel: VoiceChannel = guild.get_channel(
            private_room.move_channel_id)
        overwrite: PermissionOverwrite = move_channel.overwrites_for(
            default_role)
        overwrite.update(view_channel=False)
        await move_channel.set_permissions(default_role, overwrite=overwrite)

    # Update database
    update.pr_hidden(private_room.room_id, value=True)


async def unhide(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Unhide the private room
    :param guild: Guild of private room
    :param private_room: Private room to unhide
    """
    pr_channel: VoiceChannel = guild.get_channel(private_room.room_channel_id)
    default_role: Role = guild.default_role

    # Set permission in pr_channel
    overwrite: PermissionOverwrite = pr_channel.overwrites_for(default_role)
    overwrite.update(view_channel=True)
    await pr_channel.set_permissions(default_role, overwrite=overwrite)

    if private_room.locked:
        move_channel: VoiceChannel = guild.get_channel(
            private_room.move_channel_id)
        overwrite: PermissionOverwrite = move_channel.overwrites_for(
            default_role)
        overwrite.update(view_channel=True)
        await move_channel.set_permissions(default_role, overwrite=overwrite)

    # Update database
    update.pr_hidden(private_room.room_id, value=False)


async def toggle_visibility(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Toggle visibility of private room
    :param guild: Guild of private room
    :param private_room: Private room to change visibility
    """
    if private_room.hidden:
        # Unhide private room
        await unhide(guild, private_room)
    else:
        # Hide private room
        await hide(guild, private_room)


async def information_message(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Send direct message to the owner about the current settings of the private room
    :param guild: Guild of private room
    :param private_room: Private room to send settings of
    """
    owner: Member = guild.get_member(private_room.owner_id)

    embed: Embed = Embed(title='Your Private Room Settings', timestamp=datetime.utcnow(),
                         colour=appearance.get_color(guild.id))

    # Add information about game activity
    if private_room.game_activity:
        embed.add_field(name='Game Activity',
                        value='Game activity will be shown 🎮', inline=False)
    else:
        embed.add_field(name='Game Activity',
                        value='Game activity will not be shown', inline=False)

    # Add information about privacy status
    if private_room.locked:
        embed.add_field(
            name='Privacy', value='Currently locked 🔒', inline=False)
    else:
        embed.add_field(
            name='Privacy', value='Currently unlocked 🔓', inline=False)

    # Add information about limit
    if private_room.user_limit == 0:
        embed.add_field(
            name='Limit', value='There is no limit 🔄', inline=False)
    else:
        embed.add_field(
            name='Limit', value=f'The limit is set to `{private_room.user_limit}`', inline=False)

    # Add information about visibiltiy status
    if private_room.hidden:
        embed.add_field(
            name='Visibility', value='The room is hidden at the moment 🚫', inline=False)
    else:
        embed.add_field(
            name='Visibility', value='The room is visible at the moment 👀', inline=False)

    # Set footer
    embed.set_footer(text='Private Room', icon_url=owner.avatar_url)

    # Try to send embed
    try:
        await owner.send(embed=embed)
    except Forbidden:
        pass


async def setup_settings(guild: Guild) -> None:
    """
    Setup setting messages for the guild
    :param guild: Guild to set up setting messages
    """
    old_channel: TextChannel = private_rooms.get_settings_channel(guild)

    await asyncio.sleep(0.2)
    category: CategoryChannel = private_rooms.get_category(guild)

    # Create settings channel, set permissions and add to database
    settings_overwrites = {
        guild.default_role: PermissionOverwrite(view_channel=False, send_messages=False),
    }
    settings_channel: TextChannel = await guild.create_text_channel('settings', category=category,
                                                                    overwrites=settings_overwrites,
                                                                    reason='Setup private rooms')
    update.pr_settings_id(argument=guild.id, value=settings_channel.id)

    await asyncio.sleep(0.2)

    if old_channel:
        try:
            await old_channel.delete()
        except NotFound:
            pass

    try:
        # Send settings embed and add emoji
        settings_emebd: Embed = Embed(title='Private Room Settings', description='Here you can adjust your private room',
                                      colour=appearance.get_color(guild.id))
        settings_emebd.add_field(name='Current Settings', value='React with ℹ️ to get the current settings of your room '
                                                                'via dm')

        settings_msg: Message = await settings_channel.send(embed=settings_emebd)
        await settings_msg.add_reaction(emoji='ℹ️')

        if select.pr_change_name(guild.id):
            # Send lock embed and add emoji
            lock_embed: Embed = Embed(title='Name', description='Set the name of your private room',
                                      colour=appearance.get_color(guild.id))
            lock_embed.add_field(name='Set Name', value='React with 🪧 to change the name of your private room\n'
                                                        'You have 10 seconds time to write the new name in this text channel'
                                                        ' (20 characters maximum)')
            lock_embed.add_field(name='Toggle Game Activity', value='React with 🎮 to toggle whether the main game activity of '
                                                                    'your room is shown in the name', inline=False)

            lock_msg: Message = await settings_channel.send(embed=lock_embed)
            await lock_msg.add_reaction(emoji='🪧')
            await lock_msg.add_reaction(emoji='🎮')

        if select.pr_change_privacy(guild.id):
            # Send lock embed and add emoji
            lock_embed: Embed = Embed(title='Privacy', description='Decide whether members can join your private room or '
                                                                   'have to be moved',
                                      colour=appearance.get_color(guild.id))
            lock_embed.add_field(
                name='Toggle Privacy', value='React with 🔒 to lock or unlock your private room')

            lock_msg: Message = await settings_channel.send(embed=lock_embed)
            await lock_msg.add_reaction(emoji='🔒')

        if select.pr_change_limit(guild.id):
            # Send limit embed and add emojis
            limit_embed: Embed = Embed(title='Limit', description='Set how many users can join your channel',
                                       colour=appearance.get_color(guild.id))
            limit_embed.add_field(
                name='No Limit', value='React with 🔄 to set no user limit', inline=False)
            limit_embed.add_field(name='Limit', value='React with 🔢 to set the user limit to a specific number\n'
                                                      'You have 10 seconds time to write the new limit in this text channel',
                                  inline=False)

            limit_msg: Message = await settings_channel.send(embed=limit_embed)
            await limit_msg.add_reaction(emoji='🔄')
            await limit_msg.add_reaction(emoji='🔢')

        if select.pr_change_visibility(guild.id):
            # Send hide embed and add emoji
            hide_embed: Embed = Embed(title='Visibility', description='Adjust whether your channel can be seen or not',
                                      colour=appearance.get_color(guild.id))
            hide_embed.add_field(
                name='Toggle Visibility', value='React with 👀 to lock or unlock your private room')

            hide_msg: Message = await settings_channel.send(embed=hide_embed)
            await hide_msg.add_reaction(emoji='👀')
    except NotFound:
        return


async def check_reactions(member: Member, guild: Guild, private_room: PrivateRoom, message: Message, emoji: str,
                          added: bool = True) -> None:
    """
    Handles the reactions added on setup messages.
    :param member: Member of reaction
    :param guild: Guild of reaction
    :param private_room: Private room of owner
    :param message: Message of reaction
    :param emoji: Emoji that was reacted
    :param added: Whether the reaction was added or removed
    """

    if message.author.id != secret.bot_id:
        # Ignore reactions on messages, that are from other ones
        return

    # Remove Reaction
    await message.remove_reaction(emoji, member)

    if member.bot:
        # Ignore reactions from bots
        return

    # Get the title of the message
    embeds = message.embeds
    if embeds:
        title = embeds[0].title
    else:
        # Return if the message isn't an embed
        return

    # Reactions added
    if added:
        # Check for the different reactions
        if title == 'Private Room Settings':
            if emoji == 'ℹ️':
                # Send information about private room via dm
                await information_message(guild, private_room)

        elif title == 'Name':
            if emoji == '🪧':
                # Set name
                await name_response(guild, private_room)
            if emoji == '🎮':
                # Toggle game activity
                await toggle_game_activity(guild, private_room)

        elif title == 'Privacy':
            if emoji == '🔒':
                # Toggle privacy
                await toggle_privacy(guild, private_room)

        elif title == 'Limit':
            if emoji == '🔄':
                # Reset limit
                await set_user_limit(0, guild, private_room)
            elif emoji == '🔢':
                # Set limit
                await limit_response(guild, private_room)

        elif title == 'Visibility':
            if emoji == '👀':
                # Deactivate moderation log
                await toggle_visibility(guild, private_room)


def set_default(guild: Guild, private_room: PrivateRoom) -> None:
    """
    Set the settings of the private room to the default ones of the guild
    :param guild: Guild to set default settings
    :param private_room: Private room to retrieve settings from
    """
    # Set the default settings
    update.default_pr_game_activity(
        argument=guild.id, value=private_room.game_activity)
    update.default_pr_locked(argument=guild.id, value=private_room.locked)
    update.default_pr_user_limit(
        argument=guild.id, value=private_room.user_limit)
    update.default_pr_hidden(argument=guild.id, value=private_room.hidden)
