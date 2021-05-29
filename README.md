# **fryselBot**

Hello friends! 
fryselBot is a great Discord bot with a lot of awesome features!
- [Features](https://github.com/Fynn-F/fryselBot#features)
  - [Private Rooms](https://github.com/Fynn-F/fryselBot#private-rooms)
  - [Moderation](https://github.com/Fynn-F/fryselBot#moderation)
  - [Welcome & Leave](https://github.com/Fynn-F/fryselBot#welcome--leave)
  - [Other Features](https://github.com/Fynn-F/fryselBot#other-features)
- [Usage](https://github.com/Fynn-F/fryselBot#usage)

# **Features**
## **Private Rooms**
Private Rooms can be created easily by any member of your server.
Just join a voice channel and a private room is created for you.
Set the settings of your private room in #settings.
Once all members leave the channel, the private room will be deleted
- Change settings for your private room
  - Change the name
  - Show the main game activity of your room
  - Lock your room
  - Hide your room
  - Set a custom user limit
- Set default private room settings for your server
- Add text channels for each room

## **Moderation**
- Moderation log
- Set custom admin and moderator roles
- Clear messages
- Mute/tempmute
- Kick
- Ban/tempban
- Warns
- Reports (Requires moderation log)

## **Welcome & Leave**
- Welcome messages on your server
- Custom welcome DMs
- Leave messages on your server

## **Other Features**
- Autorole
- Custom prefix
- Custom message color


# **Usage**
FryselBot is not public yet. But you can use the code and host fryselBot yourself! Just follow the steps below.

1. Make sure you have installed <a href="https://www.python.org/downloads/" target="_blank">Python 3.9</a>.
2. Install <a href="https://discordpy.readthedocs.io/en/latest/intro.html" target="_blank">discord.py</a> in your Terminal.
3. Create a bot account. Click <a href="https://discordpy.readthedocs.io/en/latest/discord.html" target="_blank">here</a> for additional help.
4. Activate both **Presence** and **Server Members Intents**. You can find further instructions <a href="https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents" target="_blank">here</a>.
5. Download the source code by [downloading the zip](https://github.com/Fynn-F/fryselBot/archive/refs/heads/master.zip) or cloning the repository if you have git installed (recommended). Read <a href="https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository-from-github/cloning-a-repository" target="_blank">here</a> for documentation.
6. Add the following file **`/utilities/secret.py`** and add this code:
    ```python
    # Put the Discord IDs of you and your team here
    # These IDs have access to all commands of the bot
    # Example: dev_ids = {238302406622332784,472827052372501821}
    dev_ids = {}

    # Add the Discord ID of your bot here
    # Example: bot_id = 466223327842383024
    bot_id = 

    # Token of your bot client
    bot_token = "THE TOKEN OF YOUR BOT"
    ```
7. Now you can open the Terminal or command prompt, change the directory to the source code and run the bot with **`python3 bot.py`**



