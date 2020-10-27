from datetime import datetime
import requests

from nilva_TelegramBot.config import GET_NOTIF_URL, EditingNotif, API_TOKEN_URL, EDIT_NOTIF_URL
from nilva_TelegramBot.decorators import quit, bot, crsr


@quit
def get_id_for_edit(message):
    chat_id = message.from_user.id
    id = int(message.text)

    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    username = rows[0][1]
    token = rows[0][3]
    headers = {'Authorization': f'Bearer {token}'}

    request = requests.get(GET_NOTIF_URL, headers=headers).json()
    for r in request:
        if r['id'] == id:
            if r['creator'] == username:
                EditingNotif['id'] = id
                msg = bot.send_message(chat_id, 'title')
                bot.register_next_step_handler(msg, edit_title)
                return
            else:
                bot.send_message(chat_id, 'Access Denied!')

    bot.send_message(chat_id, 'Invalid Notification ID!')


@quit
def edit_title(message):
    chat_id = message.from_user.id
    if message.text != 'none':
        EditingNotif['title'] = message.text
    msg = bot.send_message(chat_id, 'description')
    bot.register_next_step_handler(msg, edit_description)


@quit
def edit_description(message):
    chat_id = message.from_user.id
    if message.text != 'none':
        EditingNotif['description'] = message.text
    msg = bot.send_message(chat_id, 'time to send\nformat: yyyy:mm:dd:hh:mm')
    bot.register_next_step_handler(msg, edit_time_to_send)


@quit
def edit_time_to_send(message):
    global time_to_send
    chat_id = message.from_user.id
    try:
        time_to_send = datetime.strptime(message.text, '%Y:%m:%d:%H:%M')
    except ValueError as e:
        msg = bot.send_message(chat_id, str(e))
        bot.register_next_step_handler(msg, edit_time_to_send)
        #  does it need to return?
    if message.text != 'none':
        EditingNotif['time_to_send'] = time_to_send
    msg = bot.send_message(chat_id, 'notification types\navailable types: email, sms, bot notif, firebase\nexample: '
                                    'bot notif, sms')
    bot.register_next_step_handler(msg, edit_notif_types)


@quit
def edit_notif_types(message):
    chat_id = message.from_user.id
    notif_types = message.text.split(', ')
    if message.text != 'none':
        EditingNotif['notification_types'] = notif_types
    msg = bot.send_message(chat_id, 'repeat and interval\nformat: <repeat> <interval> (you can use <none> for each '
                                    'one\nyou can use -1 for repeat for infinite endless notifications (and you may '
                                    'delete it later)')
    bot.register_next_step_handler(msg, edit_repeat_interval)


@quit
def edit_repeat_interval(message):
    chat_id = message.from_user.id
    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    username, password = rows[0][1], rows[0][2]
    request = requests.post(API_TOKEN_URL, data={'username': username, 'password': password}).json()
    token = request['access']

    repeat, interval = message.text.split(' ')
    if repeat != 'none':
        EditingNotif['repeat'] = int(repeat)
    if interval != 'none':
        EditingNotif['interval'] = int(interval)

    data = {}
    for key in EditingNotif:
        if EditingNotif[key] is not None:
            data[key] = EditingNotif[key]
            EditingNotif[key] = None

    requests.patch(EditingNotif, data, headers={'Authorization': f'Bearer {token}'})
    bot.send_message(chat_id, 'Successful Operation')
