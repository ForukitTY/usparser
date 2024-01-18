import logging
import os
import requests
from datetime import datetime

from USPparser import sem_parser
from dbConnect import add_to_db, get_from_db, users_count

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext.filters import MessageFilter

from dotenv import load_dotenv

url = 'https://usp.kbsu.ru/getinfo.php'

load_dotenv()
token = os.getenv('token')
admin_id = os.getenv('admin_id')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding="UTF-8",
    filename=r'.\logs.log'
)

#TODO: 1. Добавить описание к функциям и аннотации
#TODO: 2. Не обновлять данные в бд после каждого сообщения "Фамилия Зачетка", а только через login (за исключением первого запуска бота)


class FilterMyData(MessageFilter):  # ловит логин (ввод фамилии и зачетки)
    def filter(self, message):
        txt = message.text.split()
        return len(txt) == 2 and isinstance(txt[0], str) and txt[1].isdigit()


class FilterSemestr(MessageFilter):  # цифра в чат = вернуть семестр по ней
    def filter(self, message):
        txt = message.text.split()
        return len(txt) == 1 and txt[0].isdigit()


class FilterLastSem(MessageFilter):
    def filter(self, message):
        return 'Последний семестр' in message.text


class FilterAnotherSem(MessageFilter):
    def filter(self, message):
        return 'Другой семестр:' in message.text


class FilterWeek(MessageFilter):
    def filter(self, message):
        return 'Неделя' in message.text


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Неизвестная команда. Вот возможные:\n/login   Фамилия   Зачетка'
                                        '\n/usp - вернет баллы за последний семестр'
                                        '\nМожешь просто отправить номер семестра, который нужно вывести'
                                   )


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"user: {update.message.from_user.id, update.effective_user.full_name} запросил неделю.")
    week_state = "Верхняя" if datetime.now().isocalendar()[1] % 2 == 1 else "Нижняя"
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"{datetime.now().date()}\n-{week_state} неделя"
                                   )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"bot was started by user: {update.message.from_user.id, update.effective_user.full_name}")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_markup=ReplyKeyboardRemove(),
                                   text="Бот который быстро покажет баллы с сайта usp.kbsu\n\n"
                                        "Сейчас введи свою фамилию и номер зачетки, чтобы больше не логиниться:"
                                   )


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        txt = update.message.text.split()
        fam, num = txt[0], txt[1]
    except:
        text = 'Введите свою фамилию и номер зачетки:'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return 0

    req = requests.post(url, data={'c_fam': fam, 'tabn': num})

    if req.text == 'Не найден студент с такими данными':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Такой студент не найден.\n'
                                            f'Введите свой логин и зачетку еще раз:')
        return 0

    add_to_db(int(update.effective_user.id), str(fam), int(num))
    reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup,
                                   text=f'Все. Поехали! Используй кнопочки ⬇️')

    await context.bot.send_message(chat_id=admin_id, text=f"Иу у нас +1 пользовтель. Теперь нас {users_count()}")


async def usp(update: Update, context: ContextTypes.DEFAULT_TYPE):

    fam, num = get_from_db(update.effective_user.id)

    if context.args == None and (fam, num) == (None, None):  # юзер не логинился - и его нет в базе
        logging.info(f"TgUser: {update.effective_user.id, update.effective_user.full_name} не найден в базе и не написал данные после /usp")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Вы не ввели данные для входа на сайт usp.kbsu\n'
                                            'Отправьте мне фамилию и номер зачетки')
        return 0

    else:  # юзер логинился - он есть в базе

        req = requests.post(url, data={'c_fam': fam, 'tabn': num})

        if req.text == 'Не найден студент с такими данными':   # мог ввести неверно
            logging.info(f"TgUser: {update.effective_user.id, update.effective_user.full_name} не найден в базе и написал неверные данные для логина на сайт")
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Кажется ты ввел неверные данные для входа на сайт.\n'
                                           f'Попробуй еще раз по шаблону /usp Иванов 1234567')
            return 0
        else:  # баллы найдены на сайте

            semestr = int(update.message.text) if update.message.text.isdigit() else 0  # если ввел цифру-семестр, иначе отдаем последний семестр
            reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_markup=reply_markup,
                                           text=f'Итоговые баллы за {"последний" if semestr==0 else semestr} семестр: {fam}\n\n{sem_parser(req.text, semestr=semestr)}')
            logging.info(f'TgUser: {update.effective_user.id, update.effective_user.full_name}, получил баллы за {"последний" if semestr==0 else semestr} семестр')


async def another_sem_input_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f'Введи номер нужного семестра: \n')

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()

    button_list = [
        [
            KeyboardButton("Последний семестр"),
        ],
        [
            KeyboardButton("Другой семестр:"),
        ],
        [
            KeyboardButton("Неделя"),
        ]
    ]

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    filter_my_data = FilterMyData()  # ловит логин (ввод фамилии и зачетки)
    my_data_handler = MessageHandler(filter_my_data, login)
    application.add_handler(my_data_handler)

    filter_week = FilterWeek()  # ловит кнопку "Неделя"
    week_handler = MessageHandler(filter_week, week)
    application.add_handler(week_handler)

    filter_last_sem_marks = FilterLastSem()  # ловит кнопку "Последний семестр"
    last_sem_marks_handler = MessageHandler(filter_last_sem_marks, usp)
    application.add_handler(last_sem_marks_handler)

    filter_another_sem_marks = FilterAnotherSem()  # ловит кнопку "Другой семестр:"
    another_sem_marks_handler = MessageHandler(filter_another_sem_marks, another_sem_input_num)
    application.add_handler(another_sem_marks_handler)

    filter_sem = FilterSemestr()   # ловит номер семестра
    semestr_handler = MessageHandler(filter_sem, usp)
    application.add_handler(semestr_handler)

    login_handler = CommandHandler('login', login)
    application.add_handler(login_handler)

    usp_handler = CommandHandler('usp', usp)
    application.add_handler(usp_handler)

    message_handler = MessageHandler(~filter_my_data & filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(message_handler)

    application.run_polling()
