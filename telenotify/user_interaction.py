import time
import requests
from datetime import datetime

from telenotify import telegram_bots

MAX_RETRY = 10
MAX_WAIT = 60
INCREMENT_WAIT = 1
offset = None
chats = []

WEB_URL = "https://api.telegram.org/bot"

def log_error(msg):
    now = datetime.now()
    timestamp = f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}:{now.second}"
    print(f"[{timestamp}]{msg.strip()}")


def post_request(method,data,files=None):
    global WEB_URL
    try:
        return requests.post(f"{WEB_URL}{telegram_bots.get_token()}/{method}",data=data, files=files)
    except requests.exceptions.Timeout:
        return 'Timeout'
    except requests.exceptions.TooManyRedirects:
        return '2Redir'
    except requests.ConnectionError as e:
        if 'MaxRetryError' not in str(e.args) or 'NewConnectionError' not in str(e.args):
            return 'DNS_DOWN'
        if "[Errno 8]" in str(e) or "[Errno 11001]" in str(e) or "[Errno -2]" in str(e):
            return 'DNS_DOWN'
        else:
            return 'conn_error' 

def get_next_message():
    global offset
    global chats
    if len(chats) != 0:
        return chats.pop(0)
    offset = get_last_offset()
    r = post_request("getUpdates",data={"offset": offset})
    if type(r) == str:
        #exception occurred
        log_error(f"Exception:{r}")
        return False
    else:
        if r.status_code != 200:
            log_error(f"HTTP error:{r.status_code}")
            return False
    results = r.json()['result']
    for result in results:
        if result['update_id'] >= int(offset):
            offset = result['update_id'] + 1
            #stickers, emoji, etc
            if 'message' not in result:
                log_error(f"Message missing from response:{result}")
                continue
            chats.append(result['message'])
    
    if len(chats) == 0:
        return True
    return chats.pop(0) 

        

def get_request(method,params=''):
    global WEB_URL
    try:
        return requests.get(f"{WEB_URL}{telegram_bots.get_token()}/{method}?{params}")
    except requests.exceptions.Timeout:
        return 'Timeout'
    except requests.exceptions.TooManyRedirects:
        return '2Redir'
    except requests.ConnectionError as e:
        if 'MaxRetryError' not in str(e.args) or 'NewConnectionError' not in str(e.args):
            return 'DNS_DOWN'
        if "[Errno 8]" in str(e) or "[Errno 11001]" in str(e) or "[Errno -2]" in str(e):
            return 'DNS_DOWN'
        else:
            return 'conn_error'


def send_broadcast(message,bot_name=None, parse_mode=None):
    telegram_bots.select_bot(bot_name)
    for chat in telegram_bots.chats_list:
        send_notification(message, bot_name=bot_name,nickname=chat, parse_mode=parse_mode)


def send_notification(message, bot_name=None,nickname=None, parse_mode=None):
    if message is None or message == '':
        raise Exception('Empty messages not allowed')
    message = message.strip()
    telegram_bots.select_bot(bot_name)
    telegram_bots.select_chat(nickname)
    chat_id = telegram_bots.get_chat()
    data = {}
    data["chat_id"] = chat_id
    data["text"] = message
    data["disable_web_page_preview"] = True
    if parse_mode is not None:
        data["parse_mode"]=parse_mode
    return post_request("sendMessage", data)
    #return get_request("sendMessage",f"chat_id={chat_id}&text={message}")


def polling(bot_name=None, user_reminder = 0, max_wait=MAX_WAIT, incremental_wait=INCREMENT_WAIT, parse_mode=None):
    global MAX_RETRY

    telegram_bots.select_bot(bot_name)
    start_wait = 5
    wait_interval = start_wait
    cycle = 0
    fail_counts = 0
    while True:
        result = get_next_message()
        
        if result == False:
            #error occurred
            wait_interval = max_wait
            fail_counts = fail_counts + 1
            if fail_counts > MAX_RETRY:
                log_error("Cancelling polling")
                return None
        else:
            #meaning it has a message
            if result != True:
                fail_counts = 0
                wait_interval = start_wait
                cycle = 0
                if 'text' not in result:
                    log_error(f"Message missing from response:{result}")
                    continue
                if result['from']['username'] == telegram_bots.get_auth_user():
                    return result['text']

        time.sleep(wait_interval)
        if wait_interval < max_wait:
            wait_interval = cycle * incremental_wait
            if wait_interval > max_wait:
                wait_interval = max_wait
        cycle = cycle + 1

        if user_reminder > 0:
            if cycle%user_reminder == 0:
                send_notification(prompt, parse_mode=parse_mode)

def sendDocument(document_path, bot_name=None):
    telegram_bots.select_bot(bot_name)
    document = open(document_path, 'rb')
    r = post_request("sendDocument", data={'chat_id': telegram_bots.get_chat()}, files={'document': document})
    document.close()
    return r


def question(prompt, bot_name=None, user_reminder = 0, max_wait=MAX_WAIT, incremental_wait=INCREMENT_WAIT, flush=False, parse_mode=None):
    global MAX_WAIT
    global MAX_RETRY
    if flush:
        flush_chat()
    try_count = 0
    while True:
        try_count = try_count + 1
        r = send_notification(prompt, bot_name=bot_name, parse_mode=parse_mode)
        if type(r) == str:
            log_error(f"Failure asking:{prompt}\n{r}")
            if MAX_RETRY > try_count:
                raise Exception("Exceeded tries")
            time.sleep(MAX_WAIT)
            continue
        return polling(bot_name=bot_name, user_reminder = user_reminder, max_wait=max_wait, incremental_wait=incremental_wait, parse_mode=parse_mode)


def get_last_offset():
    global offset
    global chats
    if len(chats) != 0 and offset != None:
        return offset
    #only necessary for the first run
    if offset is None:
        r = get_request("getUpdates")
        results = r.json()['result']
        offset = 0
        if len(results) > 0:
            for result in results:
                offset = result['update_id'] + 1
    return offset


def flush_chat():
    global chats
    global offset
    offset = None
    chats = []


#will wait for a response from the user and return the string of that choice
def wait_for_choice(options, prompt="waiting for user's choice", bot_name=None, secret=False, prefix_msgs='Choice:', user_reminder = 0, parse_mode=None):
    if options is None or len(options) == 0:
        raise Exception("Options are a mandatory array for the wait_for_choice")

    msg = f"{prefix_msgs} {prompt}"
    if secret is False:
        wait_for_msg = str(options)[2:-2]
        wait_for_msg = wait_for_msg.replace("', '",'/')
        msg = msg + f" ({wait_for_msg})"

    #camel case option Yes/No/Cancel/nOne - will work with Y/N/C/O
    short_options = {}
    for option in options:
        if option.isupper() == False:
            for char in option:
                if char.isupper() and char not in options and char not in short_options:
                    short_options[char] = option

    while True:
        response = question(prompt=msg, bot_name=bot_name, user_reminder=user_reminder, parse_mode=parse_mode)
        if response in options or response in short_options:
            if response not in options:
                response = short_options[response]
            send_notification(f"{prefix_msgs} {response}.")
            return response
        else:
            message = f'{prefix_msgs} Not an option'
            if secret == False:
                message = message + f' ({wait_for_msg})'
            send_notification(message, parse_mode=parse_mode)


#wait for a single response, like a pause
def wait_for_user(wait_for_msg = 'K',prompt='Waiting for user to proceed', bot_name=None, prefix_msgs='Bot:', user_reminder = 180):
    flush_chat()
    wait_for_choice([wait_for_msg], prompt=prompt, bot_name=None, secret=False, prefix_msgs=prefix_msgs, user_reminder=user_reminder)


#wait for any message, like a pause
def wait_any(prompt='Waiting any input to proceed.', prefix_msgs='Bot:', bot_name=None ,done_msg=None):
    flush_chat()
    response, offset = question(prompt=prompt, bot_name=bot_name, user_reminder=0)
    if done_msg is not None and done_msg != '':
        send_notification(done_msg)
    return response

