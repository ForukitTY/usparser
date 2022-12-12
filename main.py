import requests
import json
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from USPparser import sem_parser

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
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="тут надо ввести свои данные"
                                   )
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text, reply_markup=reply_markup)


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



def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

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
        #InlineKeyboardButton("col2", callback_data='2'),
    ]

    start_handler = CommandHandler('start', start)
    my_data_handler = MessageHandler('Мои данные', my_data)

    application.add_handler(start_handler)

    application.run_polling()