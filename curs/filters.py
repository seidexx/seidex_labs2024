"""Цей файл зберігає створені фільтри для команд, що стосуються модерування чатів"""

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import config

class IsOwnerFilter(BoundFilter):
    """
    Фільтр, що вказує на власника бота, бот розуміє це за збереженим у конфіг файлі ід власника
    """
    key = "is_owner"

    def __init__(self, is_owner):
        self.is_owner = is_owner
    
    async def check(self, message: types.Message):
        return message.from_user.id == config.BOT_OWNER

class IsAdminFilter(BoundFilter):
    """
    Фільтр перевіряє чи є у учасника чату права адміністратора
    """
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() == self.is_admin


class MemberCanRestrictFilter(BoundFilter):
    """
    Фільтр перевіряє чи є серед прав адміністратора учасника право на обмеження користувачів
    """
    key = 'member_can_restrict'

    def __init__(self, member_can_restrict: bool):
        self.member_can_restrict = member_can_restrict

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)

        # Тут додатково вказано варіант, коли учасник є власником в чаті. Чомусь в цьому випадку телеграм вважав,
        # що такий учасник не має прав на обмеження інших
        return (member.is_chat_creator() or member.can_restrict_members) == self.member_can_restrict
