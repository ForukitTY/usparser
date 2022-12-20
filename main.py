import logging
import requests

from USPparser import sem_parser
from dbConnect import add_to_db, get_from_db
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
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
        txt = message.text.lower().split()
        return len(txt) == 2 and isinstance(txt[0], str) and txt[1].isdigit()


class FilterSemestr(MessageFilter):  # тип в чат цифру пишет, а я ему баллы за этот семак сразу
    def filter(self, message):
        txt = message.text.lower().strip()
        return len(txt) == 1 and txt[0].isdigit()


class FilterMyUsp(MessageFilter):
    def filter(self, message):
        return 'Мои баллы' in message.text


admin_id = 769578713
url = 'https://usp.kbsu.ru/getinfo.php'

with open('tok.txt','r') as f:
    token = f.read()


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)
    reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Неизвестная команда. Вот возможные:\n',
                                   reply_markup=reply_markup
                                   )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_markup=ReplyKeyboardRemove(),
                                   text="Бот который быстро покажет баллы с сайта usp.kbsu\n\n"
                                        "Введите свою фамилию и номер зачетки:"
                                   )


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        #await context.bot.send_message(chat_id=update.effective_chat.id,text=f'TRY LOGIN {update.message.text[0], type(update.message.text[1])}')
        txt = update.message.text.split()
        fam, num = txt[0], txt[1]
    except:
        text = 'Введите свою фамилию и номер зачетки "Иванов 1234567":'
        await context.bot.send_message(chat_id=update.effective_chat.id,text=text)
        return 0

    print(fam, num)
    req = requests.post(url, data={'c_fam': fam, 'tabn': num})

    if req.text == 'Не найден студент с такими данными':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Такой студент не найден.\n'
                                            f'Введите еще раз по шаблону "Иванов 1234567"')
        return 0

    add_to_db(int(update.effective_user.id), str(fam), int(num))
    reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup,
                                   text=f'Отлично. Теперь ты можешь сразу посмотреть свои баллы кнопкой USP')


async def usp(update: Update, context: ContextTypes.DEFAULT_TYPE, semestr = -1):
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
            KeyboardButton("Мои баллы"),  # и как сюда input данных въебать?
        ]


    ]
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    filter_my_data = FilterMyData()
    my_data_handler = MessageHandler(filter_my_data, login)
    application.add_handler(my_data_handler)

    filter_my_usp = FilterMyUsp()
    my_usp_handler = MessageHandler(filter_my_usp, usp)
    application.add_handler(my_usp_handler)

    login_handler = CommandHandler('login', login)
    application.add_handler(login_handler)

    usp_handler = CommandHandler('usp', usp)
    application.add_handler(usp_handler)

    message_handler = MessageHandler(~filter_my_data & filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(message_handler)
    application.run_polling()
