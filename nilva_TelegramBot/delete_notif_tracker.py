import requests

from nilva_TelegramBot.decorators import quit
from .config import DeletingNotif, bot, crsr, API_TOKEN_URL, GET_NOTIF_URL, EDIT_NOTIF_URL


@quit
def get_id_for_delete(message):
    chat_id = message.from_user.id
    id = int(message.text)
    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    username, password = rows[0][1], rows[0][2]
    request = requests.post(API_TOKEN_URL, data={'username': username, 'password': password}).json()
    token = request['access']
    headers = {'Authorization': f'Bearer {token}'}
    request = requests.get(GET_NOTIF_URL, headers=headers).json()

    for notif in request:
        if notif['id'] == id:
            if username in notif['relevant_staff'].split(', '):
                DeletingNotif['id'] = id
                msg = bot.send_message(chat_id, 'Are You Sure You Want To Delete This Notification\nAnswer <yes/no>??')
                bot.register_next_step_handler(msg, sure_for_delete, notif=notif)
                return
            else:
                msg = bot.send_message(chat_id, 'Access denied!')
                bot.register_next_step_handler(msg, get_id_for_delete)
                return

    bot.send_message(chat_id, 'Invalid Notification ID!')


@quit
def sure_for_delete(message, **kwargs):
    chat_id = message.from_user.id
    insert_with_params = """SELECT * FROM User WHERE chat_id = (?);"""
    data_tuple = (chat_id,)
    crsr.execute(insert_with_params, data_tuple)
    rows = crsr.fetchall()
    username, password = rows[0][1], rows[0][2]
    request = requests.post(API_TOKEN_URL, data={'username': username, 'password': password}).json()
    token = request['access']
    notif = kwargs['notif']
    revised_relevant_staff = notif['relevant_staff'].replace(username, '')
    revised_relevant_staff = revised_relevant_staff.replace(', ,', ',')

    if message.text.lower() == 'yes':
        data = {'id': notif['id'], 'relevant_staff': revised_relevant_staff}
        requests.patch(EDIT_NOTIF_URL, data, headers={'Authorization': f'Bearer {token}'})

        bot.send_message(chat_id, 'Successful Operation')