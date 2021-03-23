import asyncio
from sqlite3 import Cursor
from typing import Optional

from discord import Member, TextChannel, Message, PermissionOverwrite

from database import select, update, insert, delete
from database.manager import DatabaseEntryError, connection
from database.select import WaitingResponse


def is_waiting_for_response(member: Member, channel: TextChannel) -> bool:
    """

    :param member:
    :param channel:
    :return:
    """
    if (member.id, channel.id) in select.all_waiting_for_response():
        return True
    else:
        return False


def set_response(response: str, response_waiting: WaitingResponse) -> None:
    """
    
    :param response:
    :param response_waiting: 
    :return: 
    """
    update.response(argument=response_waiting.id, value=response)


def handle_response(message: Message) -> None:
    """

    :param message:
    :return:
    """
    channel: TextChannel = message.channel
    member = message.author

    # Check whether it was waiting for a response
    if is_waiting_for_response(member, channel):
        # Set the response
        response = message.content
        response_waiting = select.WaitingResponse(channel_id=channel.id, user_id=member.id)
        set_response(response, response_waiting)


async def wait_for_response(member: Member, channel: TextChannel, seconds: int,
                            handle_permission: bool = False) -> Optional[str]:
    """

    :param member:
    :param channel:
    :param seconds:
    :param handle_permission:
    :return:
    """
    if handle_permission:
        overwrite: PermissionOverwrite = channel.overwrites_for(member)
        overwrite.update(send_messages=True)
        await channel.set_permissions(member, overwrite=overwrite)

    # Delete old waiting for responses
    @connection
    def delete_waiting_reponses(_c: Cursor):
        _c.execute('DELETE FROM waiting_for_responses WHERE user_id=? AND channel_ID=?', (member.id, channel.id))
    delete_waiting_reponses()

    # Insert into database
    waiting_id = insert.waiting_for_reponse(member.id, channel.id, channel.guild.id)

    response = None

    # Look for response
    for _ in range(seconds):
        # Wait a second
        await asyncio.sleep(1)

        # Check whether there is a response
        try:
            waiting_response: WaitingResponse = select.WaitingResponse(id=waiting_id)
        except DatabaseEntryError:
            # Return None if the database entry was deleted
            return None

        if waiting_response.response:
            response = waiting_response.response
            break

    if handle_permission:
        overwrite: PermissionOverwrite = channel.overwrites_for(member)
        overwrite.update(send_messages=False)
        await channel.set_permissions(member, overwrite=overwrite)

    # Delete entry and return the response
    delete.waiting_for_response(id)
    return response

