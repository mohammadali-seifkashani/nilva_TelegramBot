from telebot import TeleBot
from datetime import datetime, timedelta
import requests
import sqlite3

import tracker


TOKEN = '1254140072:AAEpWrOpCmQM4DZ-RIO00i1tcK5QslbKU6Q'
bot = TeleBot(TOKEN)

AuthUser = {'username': None, 'password': None, 'chat_id': None, 'token': None}
NewNotif = { 'title': None, 'description': None, 'time_to_send': None, 'notification_types': None, 'repeat': None,
    'interval': None}
EditingNotif = {'id': None, 'title': None, 'description': None, 'time_to_send': None, 'notification_types': None,
                'repeat': None, 'interval': None}
DeletingNotif = {'id': None}

# create a database connection to a SQLite database
conn = None
try:
    conn = sqlite3.connect('nilvabotsqlite.db')
except sqlite3.Error as e:
    print(e)

crsr = conn.cursor()

# conn.execute('''
# CREATE TABLE IF NOT EXISTS User (
# chat_id integer PRIMARY KEY,
# username text,
# password text,
# token text
# );
# ''')
#
# conn.execute('''
# CREATE TABLE IF NOT EXISTS NewNotif (
# id integer PRIMARY KEY,
# title text,
# description text,
# time_to_send date,
# notification_types text,
# repeat integer,
# interval integer
# );
# ''')
#
# conn.execute('''
# CREATE TABLE IF NOT EXISTS EditingNotif (
# id integer PRIMARY KEY,
# title text,
# description text,
# time_to_send date,
# notification_types text,
# repeat integer,
# interval integer
# );
# ''')
#
# conn.execute('''
# CREATE TABLE IF NOT EXISTS DeletingNotif (
# id integer PRIMARY KEY
# );
# ''')


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
    msg = bot.send_message(chat_id, 'Username')
    bot.register_next_step_handler(msg, get_username)


def get_username(message):
    chat_id = message.from_user.id
    username = message.text

    AuthUser['username'] = username
    msg = bot.send_message(chat_id, 'Password')
    bot.register_next_step_handler(msg, get_password)


def get_password(message):
    chat_id = message.from_user.idpass
    password = message.text
    AuthUser['password'] = password
    data = {'username': AuthUser['username'], 'password': AuthUser['password']}
    request = requests.post('http://127.0.0.1:8000/api/token/', data).json()
    if not 'access' in request:
        bot.send_message(chat_id, request)
        return

    AuthUser['token'] = request['access']

    insert_with_params = """INSERT INTO User
                          (id, username, password, token) 
                          VALUES (?, ?, ?, ?);"""
    data_tuple = (chat_id, AuthUser['username'], AuthUser['password'], AuthUser['token'])
    crsr.execute(insert_with_params, data_tuple)
    conn.commit()


def authorize(func):
    def inner1(message):
        chat_id = message.from_user.id

        if message.text == '/quit':
            bot.send_message(chat_id, 'Process Quited!')
            return

        command = """SELECT chat_id FROM User WHERE chat_id = (?);"""
        data_tuple = (chat_id,)
        crsr.execute(command, data_tuple)
        rows = crsr.fetchall()
        if len(rows) == 1:
            requset = requests.post('http://127.0.0.1:8000/api/token/verify/', {'token':rows[0][3]}).json()
            if len(requset) == 0:
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


@bot.message_handler(commands=['get_all_notifs', ])
@authorize
def get_all_notifs(message):
    chat_id = message.from_user.id
    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    username = rows[0][1]
    token = rows[0][3]
    headers = {'Authorization': f'Bearer {token}'}

    request = requests.get('http://127.0.0.1:8000/notification/get/', headers=headers).json()

    output = []
    for r in request:
        if username in r['relevant_staff'].split(', '):
            output.append(r)

    bot.send_message(chat_id, output)


@bot.message_handler(commands=['add_notif', ])
@authorize
def add_notif(message):
    chat_id = message.from_user.id
    msg = bot.send_message(chat_id, 'title')
    bot.register_next_step_handler(msg, tracker.add_title)


# @quit
# def add_title(message):
#     chat_id = message.from_user.id
#     NewNotif['title'] = message.text
#     msg = bot.send_message(chat_id, 'description')
#     bot.register_next_step_handler(msg, add_description)
#
#
# @quit
# def add_description(message):
#     chat_id = message.from_user.id
#     NewNotif['description'] = message.text
#     msg = bot.send_message(chat_id, 'time to send\nformat: yyyy:mm:dd:hh:mm')
#     bot.register_next_step_handler(msg, add_time_to_send)
#
#
# @quit
# def add_time_to_send(message):
#     global time_to_send
#     chat_id = message.from_user.id
#     try:
#         time_to_send = datetime.strptime(message.text, '%Y:%m:%d:%H:%M')
#     except ValueError as e:
#         msg = bot.send_message(chat_id, str(e))
#         bot.register_next_step_handler(msg, add_time_to_send)
#     NewNotif['time_to_send'] = time_to_send
#     msg = bot.send_message(chat_id, 'notification types\navailable types: email, sms, bot notif, firebase\nexample: '
#                                     'bot notif, sms')
#     bot.register_next_step_handler(msg, add_notif_types)
#
#
# @quit
# def add_notif_types(message):
#     chat_id = message.from_user.id
#     notif_types = message.text.split(', ')
#     NewNotif['notification_types'] = notif_types
#     msg = bot.send_message(chat_id, 'repeat and interval\nformat: <repeat> <interval>\nyou can use -1 for repeat for '
#                                     'infinite endless notifications (and you may delete it later)')
#     bot.register_next_step_handler(msg, add_repeat_interval)
#
#
# @quit
# def add_repeat_interval(message):
#     chat_id = message.from_user.id
#     repeat, interval = message.text.split(' ')
#     NewNotif['repeat'] = repeat
#     NewNotif['interval'] = interval
#     bot.send_message(chat_id, 'Successful Operation')
#     url = 'http://127.0.0.1:8000/notification/add/'
#     data = {
#         'title': NewNotif['title'],
#         'description': NewNotif['description'],
#         'creator': AuthUser['username'],
#         'relevant_staff': [AuthUser['username']],
#         'time_created': datetime.now(),
#         'buffer_time': NewNotif['time_to_send'] - timedelta(hours=24),
#         'time_to_send': NewNotif['time_to_send'],
#         'notification_types': NewNotif['notification_types'],
#         'repeat': NewNotif['repeat'],
#         'interval': NewNotif['interval'],
#         'task_id': None
#     }
#     requests.post(url, data)
#
#     bot.send_message(chat_id, 'Successful Operation')


@bot.message_handler(commands=['edit_notif', ])
@authorize
def edit_notif(message):
    chat_id = message.from_user.id
    bot.send_message(chat_id, 'in each section you can type <none> for passing and not editing that')
    msg = bot.send_message(chat_id, 'id')
    bot.register_next_step_handler(msg, tracker.get_id_for_edit)


# @quit
# def get_id_for_edit(message):
#     chat_id = message.from_user.id
#     id = int(message.text)
#
#     insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
#     data_tuple = (chat_id,)
#     crsr.execute(insert_with_params, data_tuple)
#     rows = crsr.fetchall()
#     username = rows[0][1]
#
#     request = requests.get('http://127.0.0.1:8000/notification/get/').json()
#     for r in request:
#         if r['id'] == id:
#             if r['creator'] == username:
#                 EditingNotif['id'] = id
#                 msg = bot.send_message(chat_id, 'title')
#                 bot.register_next_step_handler(msg, edit_title)
#                 return
#             else:
#                 bot.send_message(chat_id, 'Access Denied!')
#
#     bot.send_message(chat_id, 'Invalid Notification ID!')
#
#
# @quit
# def edit_title(message):
#     chat_id = message.from_user.id
#     if message.text != 'none':
#         EditingNotif['title'] = message.text
#     msg = bot.send_message(chat_id, 'description')
#     bot.register_next_step_handler(msg, edit_description)
#
#
# @quit
# def edit_description(message):
#     chat_id = message.from_user.id
#     if message.text != 'none':
#         EditingNotif['description'] = message.text
#     msg = bot.send_message(chat_id, 'time to send\nformat: yyyy:mm:dd:hh:mm')
#     bot.register_next_step_handler(msg, edit_time_to_send)
#
#
# @quit
# def edit_time_to_send(message):
#     global time_to_send
#     chat_id = message.from_user.id
#     try:
#         time_to_send = datetime.strptime(message.text, '%Y:%m:%d:%H:%M')
#     except ValueError as e:
#         msg = bot.send_message(chat_id, str(e))
#         bot.register_next_step_handler(msg, add_time_to_send)
#         # does it need to return
#     if message.text != 'none':
#         EditingNotif['time_to_send'] = time_to_send
#     msg = bot.send_message(chat_id, 'notification types\navailable types: email, sms, bot notif, firebase\nexample: '
#                                     'bot notif, sms')
#     bot.register_next_step_handler(msg, edit_notif_types)
#
#
# @quit
# def edit_notif_types(message):
#     chat_id = message.from_user.id
#     notif_types = message.text.split(', ')
#     if message.text != 'none':
#         EditingNotif['notification_types'] = notif_types
#     msg = bot.send_message(chat_id, 'repeat and interval\nformat: <repeat> <interval> (you can use <none> for each '
#                                     'one\nyou can use -1 for repeat for infinite endless notifications (and you may '
#                                     'delete it later)')
#     bot.register_next_step_handler(msg, edit_repeat_interval)
#
#
# @quit
# def edit_repeat_interval(message):
#     chat_id = message.from_user.id
#     repeat, interval = message.text.split(' ')
#     if repeat != 'none':
#         EditingNotif['repeat'] = int(repeat)
#     if interval != 'none':
#         EditingNotif['interval'] = int(interval)
#     bot.send_message(chat_id, 'Successful Operation')
#
#     url = 'http://127.0.0.1:8000/notification/edit/'
#     data = {}
#     for key in EditingNotif:
#         if EditingNotif[key] is not None:
#             data[key] = EditingNotif[key]
#
#     requests.post(url, data)
#
#     bot.send_message(chat_id, 'Successful Operation')


@bot.message_handler(commands=['delete_notif', ])
@authorize
def delete_notif(message):
    chat_id = message.from_user.id
    msg = bot.send_message(chat_id, 'id')
    bot.register_next_step_handler(msg, tracker.get_id_for_delete)


# @quit
# def get_id_for_delete(message):
#     chat_id = message.from_user.id
#     id = int(message.text)
#     DeletingNotif['id'] = id
#     # msg = bot.send_message(chat_id, 'Are You Sure You Want To Delete This Notification??')
#
#     insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
#     data_tuple = (chat_id,)
#     crsr.execute(insert_with_params, data_tuple)
#     rows = crsr.fetchall()
#     username = rows[0][1]
#
#     request = requests.get('http://127.0.0.1:8000/notification/get/').json()
#     for r in request:
#         if r['id'] == id:
#             DeletingNotif['id'] = id
#             msg = bot.send_message(chat_id, 'Are You Sure You Want To Delete This Notification\nAnswer <yes/no>??')
#             bot.register_next_step_handler(msg, sure_for_delete)
#             return  # return after register_next_step_handler must be set for all functions
#
#             # if r['creator'] == username:
#             #     msg = bot.send_message(chat_id, 'Are You Sure You Want To Delete This Notification\nAnswer <yes/no>??')
#             #     bot.register_next_step_handler(msg, sure_for_delete)
#             #     return
#             # else:
#             #     bot.send_message(chat_id, 'Access Denied!')
#
#     bot.send_message(chat_id, 'Invalid Notification ID!')
#
#
# @quit
# def sure_for_delete(message):
#     chat_id = message.from_user.id
#     if message.text.lower() == 'yes':
#         url = 'http://127.0.0.1:8000/notification/delete/'
#         data = {'id': DeletingNotif['id']}
#         requests.post(url, data)
#
#         bot.send_message(chat_id, 'Successful Operation')


def send_notif(notif):
    insert_with_params = """SELECT * FROM User WHERE username IN (?);"""
    data_tuple = (notif.relevant_staff,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()

    for row in rows:
        chat_id = row[0][3]
        text = notif.title + '\n\n' + notif.description + '\n\n' + 'from Nilva Team'
        bot.send_message(chat_id, text)


bot.polling()
