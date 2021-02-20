
class Command:
    """
    Represents a command of the bot.
    Arguments:
        name         (str): Name of the command
        syntax       (str): Syntax for calling the command
        description  (str): Description of the command
        admin_only  (bool): Whether the command is for admins only
        mod_only    (bool): Whether the command is for moderators only
        hide        (bool): Whether the command is only for internal use
    Attributes:
        name         (str): Name of the command
        syntax       (str): Syntax for calling the command
        description  (str): Description of the command
        admin_only  (bool): Whether the command is for admins only
        mod_only    (bool): Whether the command is for moderators only
        hide        (bool): Whether the command is only for internal use
    """

    # TODO: Add topics to commands and have a static attribute that keeps track of them
    def __init__(self, name: str, syntax: str, description: str, admin_only: bool = False, mod_only: bool = False,
                 hide = False):
        # Initializing attributes
        self._name = name
        self._syntax = syntax
        self._admin_only = admin_only
        self._mod_only = mod_only
        self._description = description
        self._hide = hide

    # Adding properties
    name = property(lambda self: self._name)
    syntax = property(lambda self: self._syntax)
    admin_only = property(lambda self: self._admin_only)
    mod_only = property(lambda self: self._mod_only)
    description = property(lambda self: self._description)
    hide = property(lambda self: self._hide)

    # Information methods
    def member_cmd(self):
        """Returns whether the command is for members of the servers"""
        return not (self._mod_only or self._admin_only)

    def permissions_required(self) -> str:
        """Returns the permissions required to call the command"""
        perm = "nothing"
        if self._mod_only:
            perm = "moderator"
        elif self._admin_only:
            perm = "admin"
        return perm


# Description of the bot commands
commands = {Command("help", "help", "Sends a list of all commands."),
            Command("invite", "invite", "Sends an invite of the server."),
            Command("prefix", "prefix <prefix or 'default'>",
                    "Sets the server prefix to <prefix> or to the default prefix.", admin_only=True),
            Command("primary-color", "primary-color <hex-color or 'default'>",
                    "Sets the primary color of the server to <hex-color> or to the default color.", admin_only=True),
            Command("secondary-color", "secondary-color <hex-color or 'default'>",
                    "Sets the secondary color of the server to <hex-color> or to the default color.", admin_only=True),
            Command("load", "load <extension>", "Loads the extension for the bot.", admin_only=True),
            Command("unload", "unload <extension>", "Unloads the extension of the bot", hide=True)
            }


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
