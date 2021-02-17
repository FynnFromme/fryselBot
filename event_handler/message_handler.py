from discord import Message, Member, TextChannel, Guild

from fryselBot.utilities import style, secret
from fryselBot.commands import help, invite


async def new_message(message: Message):
    """Decide how to react to message.
    :param message: Message to handle
    """

    # Retrieve information about message
    member: Member = message.author
    channel: TextChannel = message.channel
    guild: Guild = message.guild
    content: str = message.content

    # Ignore messages from bots
    if member.bot:
        return

    # Help with default prefix
    if content == style.default_prefix + "help":
        await help.response(message)
        return

    # Ignore messages that aren't a command
    if not content.startswith(style.get_prefix(guild.id)):
        return
    else:
        # Edit the message content
        content = content[1:].lower()
        args = content.split()

    # Commands from here on
    # help command
    if args[0] == "help":
        await help.response(message)

    # invite command
    elif args[0] == "invite":
        await invite.response(message)

    # Test command for test purposes (only executable by frysel)
    elif args[0] == "test" and member.id == secret.frysel_id:
        from fryselBot.system import welcome_leave
        await welcome_leave.welcome_message(member)
        await welcome_leave.leave_message(member)
