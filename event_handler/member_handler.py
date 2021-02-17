from discord import Member
from fryselBot.system import welcome_leave


async def member_joined(member: Member):
    await welcome_leave.welcome_message(member)


async def member_left(member: Member):
    await welcome_leave.leave_message(member)