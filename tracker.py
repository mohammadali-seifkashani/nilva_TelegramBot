from datetime import datetime, timedelta
import requests

from main import DeletingNotif, bot, crsr, EditingNotif, AuthUser, NewNotif


def set_database(conn):
    conn.execute('''
    CREATE TABLE IF NOT EXISTS User (
    chat_id integer PRIMARY KEY,
    username text,
    password text,
    token text
    );
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS NewNotif (
    id integer PRIMARY KEY,
    title text,
    description text,
    time_to_send date,
    notification_types text,
    repeat integer,
    interval integer
    );
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS EditingNotif (
    id integer PRIMARY KEY,
    title text,
    description text,
    time_to_send date,
    notification_types text,
    repeat integer,
    interval integer
    );
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS DeletingNotif (
    id integer PRIMARY KEY
    );
    ''')


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
                                    'bot notif, sms')
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
    token = rows[0][3]

    repeat, interval = message.text.split(' ')
    NewNotif['repeat'] = repeat
    NewNotif['interval'] = interval

    url = 'http://127.0.0.1:8000/notification/add/'
    data = {
        'title': NewNotif['title'],
        'description': NewNotif['description'],
        'creator': AuthUser['username'],
        'relevant_staff': [AuthUser['username']],
        'time_created': datetime.now(),
        'buffer_time': NewNotif['time_to_send'] - timedelta(hours=24),
        'time_to_send': NewNotif['time_to_send'],
        'notification_types': NewNotif['notification_types'],
        'repeat': NewNotif['repeat'],
        'interval': NewNotif['interval'],
        'task_id': None
    }

    requests.post(url, data, headers={'Authorization': f'Bearer {token}'})

    bot.send_message(chat_id, 'Successful Operation')


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

    request = requests.get('http://127.0.0.1:8000/notification/get/', headers=headers).json()
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
    token = rows[0][3]

    repeat, interval = message.text.split(' ')
    if repeat != 'none':
        EditingNotif['repeat'] = int(repeat)
    if interval != 'none':
        EditingNotif['interval'] = int(interval)
    bot.send_message(chat_id, 'Successful Operation')

    url = 'http://127.0.0.1:8000/notification/edit/'
    data = {}
    for key in EditingNotif:
        if EditingNotif[key] is not None:
            data[key] = EditingNotif[key]

    requests.post(url, data, headers={'Authorization': f'Bearer {token}'})

    bot.send_message(chat_id, 'Successful Operation')


@quit
def get_id_for_delete(message):
    chat_id = message.from_user.id
    id = int(message.text)
    DeletingNotif['id'] = id
    # msg = bot.send_message(chat_id, 'Are You Sure You Want To Delete This Notification??')

    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    username = rows[0][1]
    token = rows[0][3]
    headers = {'Authorization': f'Bearer {token}'}

    request = requests.get('http://127.0.0.1:8000/notification/get/', headers=headers).json()
    for r in request:
        if r['id'] == id:
            DeletingNotif['id'] = id
            msg = bot.send_message(chat_id, 'Are You Sure You Want To Delete This Notification\nAnswer <yes/no>??')
            bot.register_next_step_handler(msg, sure_for_delete)
            return  # return after register_next_step_handler must be set for all functions

            # if r['creator'] == username:
            #     msg = bot.send_message(chat_id, 'Are You Sure You Want To Delete This Notification\nAnswer <yes/no>??')
            #     bot.register_next_step_handler(msg, sure_for_delete)
            #     return
            # else:
            #     bot.send_message(chat_id, 'Access Denied!')

    bot.send_message(chat_id, 'Invalid Notification ID!')


@quit
def sure_for_delete(message):
    chat_id = message.from_user.id
    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    token = rows[0][3]

    if message.text.lower() == 'yes':
        url = 'http://127.0.0.1:8000/notification/delete/'
        data = {'id': DeletingNotif['id']}
        requests.post(url, data, headers={'Authorization': f'Bearer {token}'})

        bot.send_message(chat_id, 'Successful Operation')
