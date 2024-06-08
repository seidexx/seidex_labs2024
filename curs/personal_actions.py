from aiogram import types
from dispatcher import dp
import config
import re
from bot import BotDB
import datetime
import requests
import numpy as np
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Команда початку взаємодії з ботом. При вершій активації бот додає запис про користувача у БД

@dp.message_handler(commands = "start")
async def start(message: types.Message):
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = ["/earned", "/spent", "/history", "/del"]
    keyboard.add(*buttons)

    await message.bot.send_message(message.from_user.id, "Я до ваших послуг!", reply_markup=keyboard)

# Клас ініціалізує змінну, вона необхідна, щоб запам'ятовувати операцію (+/-) відповідно до введеної команди
class op():
    oper=''

# Система станів, в даному випадку нам потрібен лише один. Реагує на команди у наступному хендлері, після чого ми
# можемо прийняти одне наступне повідомлення від користувача і стан вимкнеться
class Form(StatesGroup):
    wait4amount = State()

# Команди додавання запису про фінансову операцію у БД

@dp.message_handler(commands = ("spent", "earned", "s", "e"), commands_prefix = "/!")
async def add_operation(message: types.Message):

    cmd_variants = (('/spent', '/s', '!spent', '!s'), ('/earned', '/e', '!earned', '!e'))
    # Цикл для визначення знаку операції відповідно до того який шаблон команди було використано
    await Form.wait4amount.set()
    if message.text.startswith(cmd_variants[0]):
        op.oper='-'
    elif message.text.startswith(cmd_variants[1]):
        op.oper='+'
    else:
        return
    await message.answer("Введіть суму")

    @dp.message_handler(state=Form.wait4amount)
    async def oper_prop(message: types.Message, state: FSMContext):

        value=message.text
        await state.finish()

    # Робота API з Нацбанку. Перевіряємо чи є у повідомленні текст схожий на код валюти код валюти, отримуємо його за
    # допомогою регулярних виразів, звертаємось API до та шукаємо у циклі чи існує валюта, що відповідає нашому тексту,
    # якщо так - записуємо її курс у змінну

        try:
            currency = re.search(r"\b\D{3}\b", value).group(0)
            value = value.replace(currency, '').strip()

            nbu_data = requests.get(config.NBU_LINK).json()
            for i in range(len(nbu_data)):
                if nbu_data[i]['cc'] == currency.upper():
                    currency = nbu_data[i]['rate']
                    cur_check = True
                    break
        except AttributeError:
            cur_check = False

    # За допомогою регулярних виразів та методу replace() перевіряємо можливі неточності в написанні суми, які не є критичними і виправляємо
    # їх. Також перевіряємо чи була знайдена інформація про валюту

        if(len(value)):
            x = re.findall(r"\d+(?:.\d+)?", value)
            if(len(x)):
                value = float(x[0].replace(',', '.'))
                try:
                    if(cur_check):
                        value = value * currency
                        value = np.round(value, 2)
                except UnboundLocalError:
                    return

        #  Заносимо інформацію у БД

                BotDB.add_record(message.from_user.id, op.oper, value)

                if(op.oper == '-'):
                    await message.reply(f"✅ Запис про <u><b>витрату</b></u> {value} грн. успішно внесено!")
                else:
                    await message.reply(f"✅ Запис про <u><b>дохід</b></u> {value} грн. успішно внесено!")
            else:
                await message.reply("Не вдалось визначити суму!")
        else:
            await message.reply("Не введена сума!")


# Хендлер для перегляду історії операцій за певний період

@dp.message_handler(commands = ("history", "h"), commands_prefix = "/!")
async def history(message: types.Message):
    cmd_variants = ('/history', '/h', '!history', '!h')
    within_als = {
        "day": ('today', 'day', 'сьогодні', 'день'),
        "week": ('week', 'тиждень'),
        "month": ('month', 'місяць'),
        "year": ('year', 'рік'),
    }
# Прибираємо текст самої команди

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()

# Звіряємо позбавлену ключового слова команду з масивом можливих відрізків часу

    within = 'day'
    if(len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if(als == cmd):
                    within = k

# Викликаємо функцію відображення записаних у БД операцій за певний період. Далі виводимо їх у циклі

    records = BotDB.get_records(message.from_user.id, within)
    checkplus=0
    checkminus=0

    if(len(records)):
        answer = f"🕘 Історія операцій за {within_als[within][-1]} для {message.from_user.first_name}\n\n"

        for r in records:
            answer += "<b>" + ("➖ Витрата  " if not r[2] else "➕ Прибуток") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"
            if r[2]:
                checkplus += r[3]
            else:
                checkminus -= r[3]

        await message.reply(answer)
        await message.answer(f"⏫ Загальний прибуток за цей період {np.round(checkplus, 2)} грн.\n"
                             f"⏬ Загальна витрата за цей період {np.round(abs(checkminus), 2)} грн.\n"
                             f"💲 Загальний стан на період {np.round(checkplus+checkminus)}")

    else:
        await message.reply("Записів не знайдено!")


# Команда видаляє останній внесений даним користувачем запис у БД

@dp.message_handler(commands = ("del"), commands_prefix = "/!")
async def delete(message: types.Message):

# Викликаємо функцію, що дає нам список id записів з БД. У циклі шукаємо, який id є найбільшим, а отже належить
# останньому внесеному запису. Після циклу передаємо отримані дані у функцію, що видалить вибраний запис у БД

    list = BotDB.give_id_list(message.from_user.id)
    id=0
    for i in list:
        for j in i:
            if j>id:
                id=j
            else:
                break

    BotDB.del_record(message.from_user.id, id)
    await message.reply("🚮 Запис видалено!")

# Команда, що відноситься до можливостей модерації чату і обмежує можливість користувача відправляти повідомлення
# протягом вказаного терміну у секундах. (Лише для адмінів з правом обмеження користувачів)

@dp.message_handler(is_admin=True, member_can_restrict=True ,commands="ban", commands_prefix="!/")
async def ban(message: types.Message):
    cmd_variants = ('!ban', '/ban')
    if not message.reply_to_message:
        await message.answer("Цю команду потрібно відправляти у відповідь на повідомлення!")
        return

# Вирізаємо текст команди з повідомлення, частину, що залишилась перевіряємо на можливість перетворення на
# цілочисельну змінну, використовуємо бібліотеку, щоб вказати час обмеження

    value = message.text
    for i in cmd_variants:
        value = value.replace(i, '').strip()
    try:
        value=int(value)
        bantimer = datetime.datetime.now() + datetime.timedelta(seconds=value)
        bantimer_check=True
    except ValueError:
        bantimer=None
        bantimer_check=False

    await message.bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, None, bantimer, False)

    if bantimer_check:
        await message.answer(f"Користувача обмежено до {bantimer}")
    else:
        await message.answer("Користувача обмежено")

# Команда відміняє обмеження відправки повідомлень (Лише для адмінів)

@dp.message_handler(is_admin=True, commands="free", commands_prefix="!/")
async def unban(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Цю команду потрібно відправляти у відповідь на повідомлення!")
        return
    await message.bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, None, None, True)
    await message.answer("Заборону на відправку повідомлень скасовано")

# Команда виводить довідку для користувача

@dp.message_handler(commands="help", commands_prefix="!/")
async def help(message: types.Message):
    await message.answer("Даний бот створений для модерування ваших фінансових операцій\n\n"
                         "/start - Команда для початку роботи / перезапуску. Починаючи переписку з ботом ви передаєте свій id\n"
                         "/earned - Внести запис про прибуток. Підтримується конвертація валют. Приклади "
                         "продовження для команди: 3 , 2 usd , eur 4\n"
                         "/spent - Внести запис про витрату, функціонал схожий до /earned\n"
                         "/history - Отримати записи за певний період (за замовчуванням день) "
                         "Приклади: /h week , /h month , /history year\n"
                         "/del - Видалити останній запис, таким чином можна видаляти будь-яку к-сть\n\n"
                         "Також існують невеличкі можливості в сфері модерування чатів\n\n"
                         "/ban - Обмежити користувачу можливість відправляти повідомлення. Використовується у відповідь "
                         "на повідомлення користувача. Приклади: /ban 60 , /ban , !ban 300\n"
                         "/free - Звільнити користувача від дії команди /ban\n")