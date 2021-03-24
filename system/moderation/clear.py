from discord import Message, TextChannel, Embed, Member, Guild
from system import appearance
from system.moderation import moderation
from utilities import util


async def clear_messages(message: Message, amount: int) -> None:
    """
    Deletes the latest amount messages in the channel
    :param message: Message of command call
    :param amount: Amount of messages that should be deleted
    """
    # Delete message of member
    await util.delete_message(message)

    # Delete one message at minimum
    if amount < 0:
        amount = 0
    # Only delete 100 messages at maximum
    if amount > 100:
        amount = 100

    channel: TextChannel = message.channel
    
    # Delete the latest amount messages in the channel that are not pinned
    deleted = []
    async for msg in channel.history(limit=amount + 50):
        if not msg.pinned:
            deleted.append(msg)
            if len(deleted) == amount:
                break

    await channel.delete_messages(deleted)

    # Send confirmation and delete it after time
    await moderation.chat_message(channel, f'Successfully deleted {len(deleted)} messages',
                                  appearance.moderation_color)


async def clear_member(member: Member, message: Message, amount: int = 100) -> None:
    """
    Deletes the latest amount messages in the channel of member
    :param member: Member to delete messages of
    :param message: Message of command call
    :param amount: Amount of messages that should be deleted
    """
    # Initialize varaibles
    channel: TextChannel = message.channel

    # Delete message of member
    await util.delete_message(message)

    # Delete one message at minimum
    if amount < 0:
        amount = 0
    # Only delete 100 messages at maximum
    if amount > 100:
        amount = 100

    # Delete the latest amount messages in the channel that are from the member
    deleted = []
    async for msg in channel.history(limit=50000):
        if msg.author == member:
            deleted.append(msg)
            if len(deleted) == amount:
                break

    await channel.delete_messages(deleted)

    # Send confirmation and delete it after time
    await moderation.chat_message(channel, f'Successfully deleted {len(deleted)} messages of {member.mention}',
                                  appearance.moderation_color)
