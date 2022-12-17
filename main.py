import logging
import requests

from USPparser import sem_parser
from dbConnect import add_to_db, get_from_db
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext.filters import MessageFilter

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class TgComands: # По хорошему все команды бота тут объявить. И класс этот в другом файле должен быть
    pass


class FilterMyData(MessageFilter):
    def filter(self, message):
        return 'мои баллы' in message.text.lower()


admin_id = 769578713
url = 'https://usp.kbsu.ru/getinfo.php'

with open('tok.txt','r') as f:
    token = f.read()


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)
    reply_markup = ReplyKeyboardMarkup(button_list)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Неизвестная команда. Вот возможные:\n',
                                   reply_markup=reply_markup
                                   )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(button_list)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup,
                                   text="Бот который быстро покажет баллы с сайта usp.kbsu\n\n"
                                        "Чтобы каждый раз не логиниться - введи один раз команду /login Фамилия НомерЗачетки\n\n"
                                        "С помощью /usp Фамилия НомерЗачетки можешь искать баллы любого студента, если конечно знаешь его Фамилию и Номер зачетки."
                                   )


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        fam, num = context.args[0], context.args[1]
    except:
        text = 'Введите свою фамилию и номер зачетки:'
        await context.bot.send_message(chat_id=update.effective_chat.id,text=text)
        # как ожидать ввода??

    print(fam, num)
    req = requests.post(url, data={'c_fam': fam, 'tabn': num})

    if req.text == 'Не найден студент с такими данными':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Не нашел таког студента. Может ты ввел неверные данные для входа, либо сайт не работает. Попробуй еще раз по шаблону /login Иванов 1234567')
        return 0

    add_to_db(int(update.effective_user.id), str(fam), int(num))
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f'Отлично. Теперь ты можешь сразу посмотреть свои баллы командой /usp')


async def usp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        fam, num = context.args[0], context.args[1]
    except:  # args == []
        fam, num = get_from_db(update.effective_user.id)

    if num == None:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Вы не залогинились с помощью /login\n'
                                            'Вы не ввели данные для перехода по команде /usp\n'
                                            'Сделайте хотя бы одно из двух')
        return 0

    else:
        req = requests.post(url, data={'c_fam': fam, 'tabn': num})

        if req.text == 'Не найден студент с такими данными':
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Кажется ты ввел неверные данные для входа на сайт.\n'
                                           f'Попробуй еще раз по шаблону /usp Иванов 1234567')
            return 0
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Баллы за последний семестр: {fam}\n\n{sem_parser(req.text)}')


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    # список кнопок
    button_list = [
        [
            KeyboardButton("Мои баллы"), # и как сюда input данных въебать?
            #KeyboardButton("Баллы2"), # обязательно название кнопки должно совпадать с командой???
        ]
    ]

    filter_awesome = FilterMyData()
    awesome_handler = MessageHandler(filter_awesome, usp)
    application.add_handler(awesome_handler)

    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(message_handler)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    login_handler = CommandHandler('login', login)
    application.add_handler(login_handler)

    usp_handler = CommandHandler('usp', usp)
    application.add_handler(usp_handler)

    application.run_polling()
