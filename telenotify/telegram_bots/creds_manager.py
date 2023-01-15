import json
import os

json_file_path = 'bots_creds.json'

#get bots credentials file
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
creds_file_name = os.path.join(dir_path, json_file_path)

if os.path.exists(creds_file_name):
    #load the credentials always on import
    with open(creds_file_name, 'rb') as f:
        sobj = f.read()
    bots_jo = json.loads(sobj)
else:
    #empty file, first install
    bots_jo =  {'default_bot': '', 'user': '', 'default_chat': '', 'chats': [{}], 'bots': [{}]}

selected_bot = bots_jo["default_bot"]
selected_chat = bots_jo["default_chat"]
chats_list = bots_jo['chats'][0]

#only save creds on demand
def save_creds():
    global selected_chat
    global selected_bot
    global bots_jo
    #check if there's only one user, if so set it as default
    users_count = len(bots_jo['chats'][0].keys())
    if users_count == 1:
        selected_chat = next(iter(bots_jo['chats'][0].keys()))
        bots_jo["default_chat"] = selected_chat
    #check if there's no user and clear defaults
    if users_count == 0:
        selected_chat = ''
        bots_jo["default_chat"] = selected_chat
    #check if there's only one bot, if so set it as default
    bots_count = len(bots_jo['bots'][0].keys())
    if bots_count == 1:
        selected_bot = next(iter(bots_jo['bots'][0].keys()))
        bots_jo["default_bot"] = selected_bot
    #check if there's no user and clear defaults
    if bots_count == 0:
        selected_bot = ''
        bots_jo["default_bot"] = selected_bot
    #check if the authenticated user is in users list, if not remove
    if bots_jo['user'] is not None and bots_jo['user'] == '':
        user = bots_jo['user']
        if user not in bots_jo['chats'][0]:
            bots_jo['user'] = ''
    sobj = json.dumps(bots_jo)
    with open(creds_file_name, 'w') as f:
        f.write(sobj)


def print_info():
    print(f'Default bot: {bots_jo["default_bot"]}')
    print(f'Default user: {bots_jo["default_chat"]}')
    print(f'Authenticated user: {bots_jo["user"]}')
    print('Users:')
    for user in bots_jo['chats'][0].keys():
        print(f'\t{user}')
    print('Bots:')
    for bot in bots_jo['bots'][0].keys():
        print(f'\t{bot}')


#add or replace a token for a bot
def add_bot(name, token):
    global selected_bot
    global bots_jo
    bots_jo['bots'][0][name] = token
    save_creds()

def del_bot(name):
    global selected_bot
    global bots_jo
    if name not in bots_jo['bots'][0]:
        return
    del bots_jo['bots'][0][name]
    if bots_jo["default_bot"] == name:
        bots_jo["default_bot"] = ''
    if selected_bot == name:
        selected_bot = ''
    save_creds()


def add_user(name, id):
    global chats_list
    global bots_jo
    global selected_chat
    bots_jo['chats'][0][name] = id
    chats_list = bots_jo['chats'][0]
    save_creds()


def del_user(name):
    global selected_chat
    global bots_jo
    if name not in bots_jo['chats'][0]:
        return
    del bots_jo['chats'][0][name]
    if bots_jo["default_chat"] == name:
        bots_jo["default_chat"] = ''
    if selected_chat == name:
        selected_chat = ''
    save_creds()


def set_default_bot(name):
    global bots_jo
    if has_key(bots_jo['bots'], name) == False:
        raise Exception('Bot does not exist!')
    bots_jo["default_bot"] = name
    save_creds()


def has_key(dictlist, name):
    for user in dictlist[0].keys():
        if user == name:
            return True
    return False

def set_default_user(name):
    global bots_jo
    if has_key(bots_jo['chats'], name) == False:
        raise Exception('User does not exist!')
    bots_jo["default_chat"] = name
    save_creds()
    

def set_auth_user(name):
    global bots_jo
    found = False
    if has_key(bots_jo['chats'], name) == False:
        raise Exception('User does not exist!')
    bots_jo["user"] = name
    save_creds()


def get_token():
    return bots_jo["bots"][0][selected_bot]

def get_chat():
    return chats_list[selected_chat]

def get_select_chat():
    return selected_chat

def get_selected_bot():
    return selected_bot

def get_auth_user():
    return bots_jo['user']


def select_chat(nickname):
    global selected_chat
    if nickname is None:
        return False
    if nickname == '':
        return False
    if nickname not in chats_list:
        return False
    selected_chat = nickname
    return True


def select_bot(bot_name):
    global selected_bot
    if bot_name is None:
        return False
    if bot_name == '':
        return False
    if bot_name not in bots_jo['bots'][0]:
        return False
    selected_bot = bot_name
    return True



