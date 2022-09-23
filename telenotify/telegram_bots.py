import json

json_file_path = 'bots_creds.json'

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

#from telenotify.templates import templates  # relative-import the *package* containing the templates
import telenotify
template = pkg_resources.read_text(telenotify, json_file_path)

bots_jo = json.loads(template)

selected_bot = bots_jo["default_bot"]
selected_chat = bots_jo["default_chat"]
chats_list = bots_jo['chats'][0]

def get_token():
    return bots_jo[selected_bot][0]['TOKEN']

def get_chat():
    return chats_list[selected_chat]

def get_auth_user():
    return bots_jo['user']


def select_chat(chat_name):
    global selected_chat
    if chat_name is None:
        return False
    if chat_name == '':
        return False
    if chat_name not in chats_list:
        return False
    selected_chat = chat_name


def select_bot(bot_name):
    global selected_bot
    if bot_name is None:
        return False
    if bot_name == '':
        return False
    if bot_name not in bots_jo:
        return False
    selected_bot = bot_name