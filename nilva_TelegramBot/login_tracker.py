import requests

from nilva_TelegramBot.decorators import quit
from .config import AuthUser, API_TOKEN_URL, crsr, conn, bot


@quit
def get_username(message):
    chat_id = message.from_user.id
    username = message.text
    AuthUser['username'] = username
    msg = bot.send_message(chat_id, 'Password')
    bot.register_next_step_handler(msg, get_password)


@quit
def get_password(message):
    chat_id = message.from_user.id
    password = message.text
    AuthUser['password'] = password
    data = {'username': AuthUser['username'], 'password': AuthUser['password']}
    request = requests.post(API_TOKEN_URL, data).json()
    if not 'access' in request:
        bot.send_message(chat_id, request)
        return

    insert_with_params = """INSERT INTO User
                            (chat_id, username, password) 
                            VALUES (?, ?, ?);"""
    data_tuple = (chat_id, AuthUser['username'], AuthUser['password'])
    crsr.execute(insert_with_params, data_tuple)
    conn.commit()

    bot.send_message(chat_id, 'Successful login 😊')
