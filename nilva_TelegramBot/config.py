import sqlite3
from telebot import TeleBot

TOKEN = '1254140072:AAEpWrOpCmQM4DZ-RIO00i1tcK5QslbKU6Q'
bot = TeleBot(TOKEN)
# bot.set_my_commands(['test', 'login'])

API_TOKEN_URL = 'http://127.0.0.1:8000/api/token/'
API_VERIFY_URL = 'http://127.0.0.1:8000/api/token/verify/'

ADD_NOTIF_URL = 'http://127.0.0.1:8000/notification/add/'
EDIT_NOTIF_URL = 'http://127.0.0.1:8000/notification/edit/'
GET_NOTIF_URL = 'http://127.0.0.1:8000/notification/get/'

AuthUser = {'username': None, 'password': None, 'chat_id': None}
NewNotif = {'title': None, 'description': None, 'time_to_send': None, 'notification_types': None, 'repeat': None,
            'interval': None}
EditingNotif = {'id': None, 'title': None, 'description': None, 'time_to_send': None, 'notification_types': None,
                'repeat': None, 'interval': None}
DeletingNotif = {'id': None}

# create a database connection to a SQLite database
conn = None
try:
    conn = sqlite3.connect('nilvabotsqlite.db', check_same_thread=False)
except sqlite3.Error as e:
    print(e)

conn.execute('''
CREATE TABLE IF NOT EXISTS User (
chat_id integer PRIMARY KEY,
username text,
password text
);
''')

crsr = conn.cursor()
