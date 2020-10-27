import json
from datetime import datetime, timedelta
import requests

from nilva_TelegramBot.add_notif_tracker import add_title
from nilva_TelegramBot.config import bot, conn, crsr, AuthUser, NewNotif, EditingNotif, DeletingNotif, GET_NOTIF_URL, \
    API_TOKEN_URL
from nilva_TelegramBot.decorators import authorize
from nilva_TelegramBot.delete_notif_tracker import get_id_for_delete
from nilva_TelegramBot.edit_notif_tracker import get_id_for_edit
from nilva_TelegramBot.login_tracker import get_username


@bot.message_handler(commands=['start', ])
def start(message):
    chat_id = message.from_user.id
    bot.send_message(chat_id, 'بسم اللّه الرحمن الرحیم\n\nبرای آگاهی از امکانات ربات:\n/help')


@bot.message_handler(commands=['help', ])
def help(message):
    chat_id = message.from_user.id
    bot.send_message(chat_id, '/login\n\n/get_all_notifs\n\n/add_notif\n\n/edit_notif\n\n/delete_notif\n\n/quit ('
                              'finishing any process)')


@bot.message_handler(commands=['login', ])
def login(message):
    chat_id = message.from_user.id

    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    if len(rows) == 1:
        bot.send_message(chat_id, 'You are logged in 😊')
        return

    msg = bot.send_message(chat_id, 'Username')
    bot.register_next_step_handler(msg, get_username)


@bot.message_handler(commands=['get_all_notifs', ])
@authorize
def get_all_notifs(message):
    chat_id = message.from_user.id
    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()

    username, password = rows[0][1], rows[0][2]
    request = requests.post(API_TOKEN_URL, data={'username': username, 'password': password}).json()
    token = request['access']
    headers = {'Authorization': f'Bearer {token}'}

    request = requests.get(GET_NOTIF_URL, headers=headers).json()

    output = ''
    for r in request:
        if username in r['relevant_staff'].split(', '):
            output += '{\n'
            for key in r:
                output += '    ' + key + ' : ' + str(r[key]) + '\n'
            output += '}\n'

    bot.send_message(chat_id, output)


@bot.message_handler(commands=['add_notif', ])
@authorize
def add_notif(message):
    chat_id = message.from_user.id
    msg = bot.send_message(chat_id, 'title')
    bot.register_next_step_handler(msg, add_title)


@bot.message_handler(commands=['edit_notif', ])
@authorize
def edit_notif(message):
    chat_id = message.from_user.id
    bot.send_message(chat_id, 'in each section you can type <none> for passing and not editing that')
    msg = bot.send_message(chat_id, 'id')
    bot.register_next_step_handler(msg, get_id_for_edit)


@bot.message_handler(commands=['delete_notif', ])
@authorize
def delete_notif(message):
    chat_id = message.from_user.id
    msg = bot.send_message(chat_id, 'id')
    bot.register_next_step_handler(msg, get_id_for_delete)


def send_notif(notif):
    insert_with_params = """SELECT * FROM User WHERE username IN (?);"""
    data_tuple = (notif.relevant_staff,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()

    for row in rows:
        chat_id = row[0][3]
        text = notif.title + '\n\n' + notif.description + '\n\n' + 'from Nilva Team'
        bot.send_message(chat_id, text)


@bot.message_handler(commands=['test', ])
def test(message):
    chat_id = message.from_user.id
    msg = bot.send_message(chat_id, 'first')
    bot.register_next_step_handler(msg, test_register_next_step_handler, a=1, b=2)
    print(10000000000000000000000000000)


def test_register_next_step_handler(message, **kwargs):
    chat_id = message.from_user.id
    msg = bot.send_message(chat_id, str(kwargs))


bot.polling()
