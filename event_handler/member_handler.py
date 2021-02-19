from discord import Member
from fryselBot.system import welcome


async def member_joined(member: Member):
    await welcome.welcome_message(member)


async def member_left(member: Member):
    await welcome.leave_message(member)