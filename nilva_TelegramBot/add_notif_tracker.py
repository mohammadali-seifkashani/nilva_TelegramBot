from datetime import datetime, timedelta
import requests

from nilva_TelegramBot.login_tracker import AuthUser
from nilva_TelegramBot.decorators import quit
from .config import NewNotif, API_TOKEN_URL, ADD_NOTIF_URL, bot, crsr


@quit
def add_title(message):
    chat_id = message.from_user.id
    NewNotif['title'] = message.text
    msg = bot.send_message(chat_id, 'description')
    bot.register_next_step_handler(msg, add_description)


@quit
def add_description(message):
    chat_id = message.from_user.id
    NewNotif['description'] = message.text
    msg = bot.send_message(chat_id, 'relevant_staff\nseparating with <, >')
    bot.register_next_step_handler(msg, add_relevant_staff)


@quit
def add_relevant_staff(message):
    chat_id = message.from_user.id
    NewNotif['relevant_staff'] = message.text
    msg = bot.send_message(chat_id, 'due_date\nformat: yyyy:mm:dd:hh:mm')
    bot.register_next_step_handler(msg, add_due_date)


@quit
def add_due_date(message):
    chat_id = message.from_user.id
    NewNotif['due_date'] = message.text
    msg = bot.send_message(chat_id, 'time to send\nformat: yyyy:mm:dd:hh:mm')
    bot.register_next_step_handler(msg, add_time_to_send)


@quit
def add_time_to_send(message):
    global time_to_send
    chat_id = message.from_user.id
    try:
        time_to_send = datetime.strptime(message.text, '%Y:%m:%d:%H:%M')
    except ValueError as e:
        msg = bot.send_message(chat_id, str(e))
        bot.register_next_step_handler(msg, add_time_to_send)
    NewNotif['time_to_send'] = time_to_send
    msg = bot.send_message(chat_id, 'notification types\navailable types: email, sms, bot notif, firebase\nexample: '
                                    'bot notif, sms\nformant: like top line, separating with <, >')
    bot.register_next_step_handler(msg, add_notif_types)


@quit
def add_notif_types(message):
    chat_id = message.from_user.id
    notif_types = message.text.split(', ')
    NewNotif['notification_types'] = notif_types
    msg = bot.send_message(chat_id, 'repeat and interval\nformat: <repeat> <interval>\nyou can use -1 for repeat for '
                                    'infinite endless notifications (and you may delete it later)')
    bot.register_next_step_handler(msg, add_repeat_interval)


@quit
def add_repeat_interval(message):
    chat_id = message.from_user.id
    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    username, password = rows[0][1], rows[0][2]
    request = requests.post(API_TOKEN_URL, data={'username': username, 'password': password}).json()
    token = request['access']

    repeat, interval = message.text.split(' ')
    NewNotif['repeat'] = repeat
    NewNotif['interval'] = interval

    data = {
        'title': NewNotif['title'],
        'description': NewNotif['description'],
        'creator': AuthUser['username'],
        'relevant_staff': AuthUser['username'],
        'time_created': datetime.now(),
        'due_date': NewNotif['due_date'],
        'time_to_send': NewNotif['time_to_send'],
        'notification_types': NewNotif['notification_types'],
        'repeat': NewNotif['repeat'],
        'interval': NewNotif['interval'],
        'task_id': None
    }
    requests.post(ADD_NOTIF_URL, data, headers={'Authorization': f'Bearer {token}'})
    bot.send_message(chat_id, 'Successful Operation')
