from aiogram import executor
from dispatcher import dp
from db import BotDB
import personal_actions

# Ініціалізуємо БД
BotDB = BotDB('accountant.db')

# Виконуємо програму
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
