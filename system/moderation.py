from discord import TextChannel, Member, Embed
from fryselBot.system import appearance


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
    async for msg in channel.history(limit=50000):
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


async def kick(member, reason) -> None:
    pass
    # TODO: First set up moderation log