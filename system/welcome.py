from fryselBot.database import select
from fryselBot.system import appearance
from discord import Member, Guild, TextChannel, Embed
import random

# TODO: Setup commands for welcome/leave messages
# TODO: Welcome DM
# TODO: Add cog for welcome system


async def welcome_message(member: Member):
    if not is_set_up(member.guild, welcome=True):
        return

    guild: Guild = member.guild
    welcome_channel: TextChannel = guild.get_channel(select.welcome_channel_id(guild.id))

    welcome_messages = ["{} joined. You must construct additional pylons.",
                        "Never gonna give {} up. Never let {} down!",
                        "Hey! Listen! {} has joined!",
                        "Ha! {} has joined! You activated my trap card!",
                        "We've been expecting you, {}.",
                        "It's dangerous to go alone, take {}!",
                        "Swoooosh. {} just landed.",
                        "Brace yourselves. {} just joined the Server.",
                        "A wild {} appeared."
                        ]

    # Setup embed
    embed: Embed = Embed()
    embed.description = random.choice(welcome_messages).replace("{}", member.mention)

    # Setup embed style
    embed.colour = appearance.get_primary_color(guild.id)

    # Send embed to welcome_channel
    await welcome_channel.send(embed=embed)


async def leave_message(member: Member):
    if not is_set_up(member.guild, welcome=False):
        return

    guild: Guild = member.guild
    welcome_channel: TextChannel = guild.get_channel(select.welcome_channel_id(guild.id))

    welcome_messages = ["{} left, the party's over."]

    # Setup embed
    embed: Embed = Embed()
    embed.description = random.choice(welcome_messages).replace("{}", member.display_name)

    # Setup embed style
    embed.colour = appearance.get_secondary_color(guild.id)

    # Send embed to welcome_channel
    await welcome_channel.send(embed=embed)


def is_set_up(guild: Guild, welcome: bool) -> bool:
    """
    Checks whether welcome messages are set up properly on guild
    :param guild: Discord GuildID
    :param welcome: Whether welcome (if True) or leave (if False) is set up
    :return: Whether welcome messages are set up properly on guild
    """
    # Check whether welcome messages are activated on guild
    if welcome and not select.welcome_messages(guild.id):
        return False

    # Check whether leave messages are activated on guild
    elif not welcome and not select.leave_messages(guild.id):
        return False

    # Checks whether the welcome_channel exists
    elif select.welcome_channel_id(guild.id) not in map(lambda channel: channel.id, guild.text_channels):
        return False

    # If conditions before were False everything is set up properly
    else:
        return True
