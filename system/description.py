from difflib import SequenceMatcher
from typing import Union, Callable

from discord import Guild

from fryselBot.system.moderation import moderation


class Command:
    """
    Represents a command of the bot.
    Arguments:
        name            (str): Name of the command
        syntax          (str): Syntax for calling the command
        description     (str): Description of the command
        args_description (dict[str: str]): Description of arguments
        admin_only     (bool): Whether the command is for admins only
        mod_only       (bool): Whether the command is for moderators only
        in_help        (bool/Callable): Whether the command is in help
    Attributes:
        name            (str): Name of the command
        syntax          (str): Syntax for calling the command
        description     (str): Description of the command
        args_description (dict[str: str]): Description of arguments
        admin_only     (bool): Whether the command is for admins only
        mod_only       (bool): Whether the command is for moderators only
        in_help    (Guild -> bool): Whether the command is in help
    """

    def __init__(self, name: str, syntax: str, description: str, args_description: dict[str: str] = None,
                 admin_only: bool = False, mod_only: bool = False, support_only: bool = False,
                 in_help: Union[Callable[[Guild], bool], bool] = True):
        # Initializing attributes
        self._name = name
        self._syntax = syntax
        self._admin_only = admin_only
        self._mod_only = mod_only
        self._support_only = support_only
        self._description = description
        self._args_description = args_description
        if type(in_help) == bool:
            self._in_help = lambda x: in_help
        else:
            self._in_help = in_help

    # Information methods
    def member_cmd(self) -> bool:
        """Returns whether the command is for members of the servers"""
        return not (self._mod_only or self._admin_only or self._support_only)

    def permissions_required(self) -> str:
        """Returns the permissions required to call the command"""
        perm = 'nothing'
        if self._mod_only:
            perm = 'moderator'
        elif self._admin_only:
            perm = 'admin'
        elif self._support_only:
            perm = 'supporter'
        return perm

    def _get_argument_description(self) -> str:
        """Returns a formated description of the arguments"""
        if self._args_description:
            # Create string of argument descriptions
            lines = []
            for cmd, desc in self._args_description.items():
                lines.append(f'- {cmd}: {desc}')

            return '\n'.join(lines)
        else:
            return ''

    def get_complete_description(self) -> str:
        """Returns the description of the command with the description of the arguments"""
        if self.args_description:
            # Return description with arguments
            return self._description + '\n' + self._get_argument_description()
        else:
            return self._description

    # Adding properties
    name = property(lambda self: self._name)
    syntax = property(lambda self: self._syntax)
    admin_only = property(lambda self: self._admin_only)
    mod_only = property(lambda self: self._mod_only)
    support_only = property(lambda self: self._support_only)
    description = property(lambda self: self._description)
    args_description = property(_get_argument_description)
    in_help = property(lambda self: self._in_help)


# Description of the bot commands

commands = [  # User commands
    Command('help', 'help (command)', 'Get a list of all commands or help for a specific command.',
            {'command': 'Name of the command to get detailed help for'}),
    Command('invite', 'invite', 'Get an invite of the server.'),

    # Moderation commands
    Command('clear', 'clear <amount> (member)', 'Clear messages in the channel.',
            {'amount': 'Positive integer, at most 100',
             'member': 'User mention or name'},
            mod_only=True),
    Command('mute', 'mute <member> (reason)', 'Mute a member in the text-channels.',
            {'member': 'User mention or name',
             'reason': 'Any text'},
            mod_only=True),
    Command('tempmute', 'tempmute <member> <duration> (reason)', 'Mute a member temporarily in the text-channels.',
            {'member': 'User mention or name',
             'duration': "e.g. *'5 min'*, *'3 d'*, *'1 week'*, *'6 months'* or *'3 years'*  (5 years maximum)",
             'reason': 'Any text'},
            mod_only=True),
    Command('unmute', 'unmute <member>', 'Unmute a member on the server.',
            {'member': 'User mention or name', },
            mod_only=True),
    Command('kick', 'kick <member> (reason)', 'Kick a member from the server.',
            {'member': 'User mention or name',
             'reason': 'Any text'},
            mod_only=True),
    Command('ban', 'ban <member> (reason)', 'Ban a member on the server.',
            {'member': 'User mention or name',
             'reason': 'Any text'},
            mod_only=True),
    Command('tempban', 'tempban <member> <duration> (reason)', 'Ban a member temporarily on the server.',
            {'member': 'User mention or name',
             'duration': "e.g. *'5 min'*, *'3 d'*, *'1 week'*, *'6 months'* or *'3 years'*  (5 years maximum)",
             'reason': 'Any text'},
            mod_only=True),
    Command('unban', 'unban <user>', 'Unban a user on the server.',
            {'user': 'User mention, name or ID'},
            mod_only=True),
    Command('warn', 'warn <member> (reason)', 'Warn a member on the server.',
            {'member': 'User mention or name',
             'reason': 'Any text'},
            mod_only=True),
    Command('warns', 'warns <member>', 'Get the latest warns of a member.',
            {'member': 'User mention or name'},
            mod_only=True),
    Command('report', 'report <member> <reason>', 'Report a member of the server.',
            {'member': 'User mention or name',
             'reason': 'Any text'},
            in_help=lambda g: moderation.get_mod_log(g) is not None),
    Command('reports', 'reports <member>', 'Get the latest reports of a member.',
            {'member': 'User mention or name'},
            mod_only=True,
            in_help=lambda g: moderation.get_mod_log(g) is not None),

    # Admin commands
    Command('setup', 'setup', 'Menu to set up the bot.', admin_only=True),

    Command('prefix', 'setup prefix <prefix>', 'Set the prefix of the bot on the server.',
            {'prefix': 'Single character'},
            admin_only=True, in_help=False),
    Command('color', 'setup color <color>', "Set the color of the bot's messages on the server.",
            {'color': 'HEX color code'},
            admin_only=True, in_help=False),
    Command('welcome', 'setup welcome', 'Page to set up the welcome system.', admin_only=True, in_help=False),
    Command('welcome channel', 'setup welcome channel <text-channel>',
            'Set the channel for welcome and leave messages.',
            {'text-channel': 'Channel mention or name'},
            admin_only=True, in_help=False),
    Command('welcome dm', 'setup welcome dm <text>', 'Set the text for welcome messages via DM.',
            {'text': 'Any text (<member> will be replaced by the name of the member)'},
            admin_only=True, in_help=False),
    Command('roles', 'setup roles', 'Page to set up the roles.', admin_only=True, in_help=False),
    Command('roles add', 'setup roles add <type> <role>', 'Add the role.',
            {'type': "*'admin'*, *'moderator'* or *'supporter'*",
             'role': 'Role mention or name'},
            admin_only=True, in_help=False),
    Command('roles remove', 'setup roles remove <type> <role>', 'Remove the role.',
            {'type': "*'admin'*, *'moderator'* or *'supporter'*",
             'role': 'Role mention or name'},
            admin_only=True, in_help=False),
    Command('moderation', 'setup moderation', 'Page to set up the moderation.', admin_only=True, in_help=False),
    Command('moderation log', 'setup moderation log <text-channel>', 'Set the moderation log.',
            {'text-channel': 'Channel mention or name'},
            admin_only=True, in_help=False),
]


def get_command(name: str) -> Command:
    """
    Returns the command with the given name
    :param name: Name of the command
    :return: Command with the given name
    """
    # Search command
    for cmd in commands:
        if cmd.name == name:
            # Found command with name
            return cmd


def get_similar_command(name: str) -> tuple[bool, Command]:
    """
    Returns a command with similar name
    :param name: Name of the command
    :return: Whether it is only a suggestion and the command with similar name
    """

    # Standard response
    highest_ration = (get_command('help'), 0.0)

    # Iterate through commands and search the one with highest ratio
    for cmd in commands:
        ratio = SequenceMatcher(None, cmd.name, name).ratio()
        if ratio > highest_ration[1]:
            highest_ration = (cmd, ratio)

    # Return command if there was a good match
    if highest_ration[1] > 0.6:
        # Relativly sure that this is the command searched
        return False, highest_ration[0]
    else:
        # Unsure: suggestion
        return True, highest_ration[0]


class Function:
    """
    Represents a function of the bot.
    Arguments:
        name           (str): Name of the function
        description    (str): Description of the function
        setup_cmd  (Command): Command to set it up
    Attributes:
        name           (str): Name of the function
        description    (str): Description of the function
        setup_cmd      (str): Command to set it up
    """

    def __init__(self, name: str, description: str, setup_cmd: Command):
        # Initializing attributes
        self._name = name
        self._description = description
        self._setup_cmd = setup_cmd

    # Adding properties
    name = property(lambda self: self._name)
    description = property(lambda self: self._description)
    setup_cmd = property(lambda self: self._setup_cmd)


# Description of other functions
functions = {}
