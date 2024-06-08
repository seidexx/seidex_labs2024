import logging
from aiogram import Bot, Dispatcher
from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO)

# Перевіряємо наявність токена для бота
if not config.BOT_TOKEN:
    exit("No token provided")

# Ініціалізуємо бота
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# Активовуємо фільтри, що прописані в окремому файлі, використовуються для додаткових можливостей бота для
# модерації груп та каналів
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(MemberCanRestrictFilter)
