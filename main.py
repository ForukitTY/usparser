import requests
import json

import telegram
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from USPparser import sem_parser
from telegram.ext.filters import MessageFilter

class FilterMyData(MessageFilter):
    def filter(self, message):
        return 'мои данные' in message.text.lower()

admin_id = 769578713

with open('tok.txt','r') as f:
    token = f.read()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    reply_markup = InlineKeyboardMarkup(button_list)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Чтобы узнать баллы введите свои данные для логина один раз /usp Фамилия НомерЗачетки",
                                   reply_markup=reply_markup
                                   )


async def my_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = 'https://usp.kbsu.ru/getinfo.php'
    fam = context.args[0]
    num = context.args[1]
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="тут надо ввести свои данные"
                                   )


async def usp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = 'https://usp.kbsu.ru/getinfo.php'
    fam = context.args[0]
    num = context.args[1]
    req = requests.post(url, data={'c_fam': fam, 'tabn': num})


    if req.text == 'Не найден студент с такими данными':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Такой студент не найден, введите корректные данные для входа')
        return 0
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=sem_parser(req))


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    # список кнопок
    button_list = [
        [
        InlineKeyboardButton("Мои баллы", callback_data="йцув"),
        ],
        [
        InlineKeyboardButton("Мои баллы 2", callback_data="йцув"),
        ]
    ]

    filter_awesome = FilterMyData()
    awesome_handler = MessageHandler(filter_awesome, my_data()) # где апдейты??
    application.add_handler(awesome_handler)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # my_data_handler = MessageHandler('Мои данные', my_data)
    # application.add_handler(my_data_handler)

    call_back_handler = CallbackQueryHandler()

    application.run_polling()