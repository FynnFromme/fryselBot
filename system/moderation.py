from discord import TextChannel, Member, Embed, Guild
from fryselBot.system import appearance
from fryselBot.database import select, update
from fryselBot.utilities import secret, permission


def set_mod_log(guild: Guild, channel_id: int = None) -> None:
    """
    Set the moderation log for a guild
    :param guild: Guild to set the moderation log
    :param channel_id: Channel Id for moderation log
    """
    # Update mod log in database
    update.mod_log_id(value=channel_id, argument=guild.id)


def get_mod_log(guild: Guild) -> TextChannel:
    """
    Get the moderation log of a guild
    :param guild: Guild to get moderation log
    """
    # Get mod log ID out of database
    channel_id = select.mod_log_id(guild.id)

    # Get channel by ID
    channel = guild.get_channel(channel_id)
    return channel


async def clear(channel: TextChannel, amount: int) -> None:
    """
    Deletes the latest amount messages in the channel
    :param channel: Channel to delete messages
    :param amount: Amount of messages that should be deleted
    """
    # Delete one message at minimum
    if amount < 0:
        amount = 0
    # Only delete 100 messages at maximum
    if amount > 100:
        amount = 100

    # Increment to ignore the command call of the member
    amount += 1

    # Delete the latest amount messages in the channel that are not pinned
    deleted = []
    async for msg in channel.history(limit=amount+50):
        if not msg.pinned:
            deleted.append(msg)
            if len(deleted) == amount:
                break

    await channel.delete_messages(deleted)

    # Send confirmation and delete it after time
    embed = Embed(description=f'Deleted **{len(deleted)-1}** messages',
                  colour=appearance.red_color)

    msg = await channel.send(embed=embed)
    await msg.delete(delay=10)


async def clear_member(member: Member, channel: TextChannel, amount: int = 100) -> None:
    """
    Deletes the latest amount messages in the channel of member
    :param member: Member to delete messages of
    :param channel: Channel to delete messages
    :param amount: Amount of messages that should be deleted
    """
    # Delete one message at minimum
    if amount < 0:
        amount = 0
    # Only delete 100 messages at maximum
    if amount > 100:
        amount = 100

    # Increment amount to delete command call
    amount += 1

    # Delete the latest amount messages in the channel that are from the member
    deleted = []
    async for msg in channel.history(limit=50000):
        if msg.author == member:
            deleted.append(msg)
            if len(deleted) == amount:
                print(len(deleted))
                break

    await channel.delete_messages(deleted)

    # Send confirmation and delete it after time
    embed = Embed(description=f'Deleted **{len(deleted)-1}** messages of {member.mention}',
                  colour=appearance.red_color)

    msg = await channel.send(embed=embed)
    await msg.delete(delay=10)


async def kick(guild: Guild, channel, member: Member, reason: str = None) -> None:
    """

    :param guild:
    :param channel:
    :param member:
    :param reason:
    """
    # Oft: CommandInvokeError oder Forbidden (Missing Permissions)
    if member.id == secret.bot_id:
        # Don't kick the bot
        return
    if permission.is_mod(member=member):
        # Don't kick moderators of the server
        return

    await guild.kick(member, reason=reason)

    # Message in chat
    # Message in mod log
    await channel.send(f'Kicked {member.mention} for reason: {reason}')