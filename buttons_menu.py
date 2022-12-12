from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


# список кнопок
button_list = [
    InlineKeyboardButton("col1", callback_data=...),
    InlineKeyboardButton("col2", callback_data=...),
    InlineKeyboardButton("row 2", callback_data=...)
]

# сборка клавиатуры из кнопок `InlineKeyboardButton`
reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
# отправка клавиатуры в чат для ВЕРСИИ 13.x
bot.send_message(chat_id=chat_id, text="Меню из двух столбцов", reply_markup=reply_markup)