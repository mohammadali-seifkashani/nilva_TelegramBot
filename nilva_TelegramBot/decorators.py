from nilva_TelegramBot.config import bot, crsr


def authorize(func):
    def inner1(message):
        chat_id = message.from_user.id

        command = """SELECT * FROM User WHERE chat_id = (?);"""
        data_tuple = (chat_id,)
        crsr.execute(command, data_tuple)
        rows = crsr.fetchall()
        if len(rows) == 1:
            return func(message)

        bot.send_message(chat_id, 'Unauthorized! You should login at first please.')

    return inner1


def quit(func):
    def inner1(message):
        chat_id = message.from_user.id

        if message.text == '/quit':
            bot.send_message(chat_id, 'Process Quited!')
            return

        return func(message)

    return inner1