import os
import time
import requests
from datetime import datetime
from ilock import ILock

from telenotify.telegram_bots import creds_manager

MAX_RETRY = 100
MAX_WAIT = 120
INCREMENT_WAIT = 1
FILE_LIMIT_SIZE = 50000000
MAX_NOTIFICATION = 4092
TIMEOUT_LOCK_FLUSH = 1
SPLIT_CHARS = ['\n',' ','\t']

offset = None
chats = []

WEB_URL = "https://api.telegram.org/bot"

#only for linux
MEMORY_FILE_DIRECTORY = '/dev/shm/'

lock_directory = None
if os.path.isdir(MEMORY_FILE_DIRECTORY):
    lock_directory = MEMORY_FILE_DIRECTORY

def log_error(msg):
    now = datetime.now()
    timestamp = f"{now.year}-{now.month:02}-{now.day:02} {now.hour:02}:{now.minute:02}:{now.second:02}"
    print(f"[{timestamp}] {msg.strip()}")


def post_request(method,data,files=None):
    global WEB_URL
    try:
        return requests.post(f"{WEB_URL}{creds_manager.get_token()}/{method}",data=data, files=files)
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
        return requests.get(f"{WEB_URL}{creds_manager.get_token()}/{method}?{params}")
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
    creds_manager.select_bot(bot_name)
    for chat in creds_manager.chats_list:
        send_notification(message, bot_name=bot_name,nickname=chat, parse_mode=parse_mode, persist=True)


def send_notification(message, bot_name=None,nickname=None, parse_mode=None, disable_notification=False, persist=False):
    creds_manager.select_bot(bot_name)
    creds_manager.select_chat(nickname)
    chat_id = creds_manager.get_chat()
    data = {}
    data["chat_id"] = chat_id
    data["disable_web_page_preview"] = True
    data["disable_notification"] = disable_notification
    if message == '' or message is None:
        parse_mode = 'HTML'
        message = '<strike>No message</strike>'
    else:
        message = message.strip()
    if parse_mode is not None:
        data["parse_mode"]=parse_mode

    #message too large
    if len(message) > MAX_NOTIFICATION:
        message_part1, message_part2 = split_message(message)
        if parse_mode == 'HTML':
            #has tag, propagate it
            if message[:1] == '<':
                end_tag1 = message.find("</")
                end_tag2 = message.find(">",end_tag1) + 1
                tag_close = message[end_tag1:end_tag2]
                start_tag1 = message.find("<")
                start_tag2 = message.find(">") + 1
                tag_start = message[start_tag1:start_tag2]
                message_part1, message_part2 = split_message(message, MAX_NOTIFICATION - len(tag_close))
                message_part1 += tag_close
                message_part2 = tag_start + message_part2
        send_notification(message_part1, bot_name=bot_name,nickname=nickname, parse_mode=parse_mode, disable_notification=disable_notification, persist=persist)
        return send_notification(message_part2, bot_name=bot_name,nickname=nickname, parse_mode=parse_mode, disable_notification=disable_notification, persist=persist)
    #proceed normal message
    data["text"] = message
    if persist:
        try_count = 0
        while True:
            try_count = try_count + 1
            r = post_request("sendMessage", data)
            if type(r) == str:
                log_error(f"Failure sending message:{message}\n{r}")
                if try_count > MAX_RETRY:
                    raise Exception("Exceeded tries")
                time.sleep(MAX_WAIT)
                continue
            else:
                return r
    else:
        return post_request("sendMessage", data)
    #return get_request("sendMessage",f"chat_id={chat_id}&text={message}")

def split_message(message, limit=MAX_NOTIFICATION):
    message_p1 = message[:limit]
    message_p2 = message[limit:]
    for char in SPLIT_CHARS:
        if char in message_p1:
            limit = message_p1.rfind(char)
            message_p1 = message[:limit]
            message_p2 = message[limit:]
            break
    return message_p1.strip(), message_p2.strip()

#lock_type:
#  - None - no lock
#  - Idle - only lock when getting new messages
#  - "any other" - lock whole process until getting a new message
#timeout:
# it's cycles not time based. 
# retuns None, like an error
def polling(bot_name=None, user_reminder = 0, max_wait=MAX_WAIT, incremental_wait=INCREMENT_WAIT, parse_mode=None, prompt='??', lock_type='N', timeout=None):
    global MAX_RETRY
    if user_reminder != 0 and lock_type == 'idle':
        raise Exception("If there's a reminder it cannot be an idle poll")

    creds_manager.select_bot(bot_name)
    
    start_wait = 5
    wait_interval = start_wait
    cycle = 0
    fail_counts = 0

    if lock_type != None:
        lock_name = f"lock {creds_manager.get_select_chat()} {creds_manager.get_selected_bot()}"
        lock = ILock(lock_name, lock_directory=lock_directory)
        #NOT idle lock is for whole polling
        if lock_type != 'idle':
            lock.__enter__()
    while True:
        #verify if it's timeout break
        if timeout is not None:
            if timeout <= cycle:
                break
        #when idle polling, only lock when getting messages
        if lock_type == 'idle':
            start_time = time.time()
            lock.__enter__()
            if (time.time() - start_time) >= TIMEOUT_LOCK_FLUSH:
                #if lock time was over the timeout, flush all messages
                flush_chat()
        
        #get the message
        result = get_next_message()

        #releasing lock for idle
        if lock_type == 'idle':
            lock.__exit__(None,None,None)
        
        if result == False:
            #error occurred
            wait_interval = max_wait
            fail_counts = fail_counts + 1
            if fail_counts > MAX_RETRY:
                log_error("Cancelling polling")
                if lock_type != None and lock_type != 'idle':
                    lock.__exit__(None,None,None)
                break
        else:
            #meaning it has a message
            if result != True:
                fail_counts = 0
                wait_interval = start_wait
                cycle = 0
                if 'text' not in result:
                    log_error(f"'text' missing from response:{result}")
                    continue
                if 'username' not in result['from']:
                    log_error(f"'username' missing from response:{result}")
                    continue
                if result['from']['username'] == creds_manager.get_auth_user():
                    if lock_type != None and lock_type != 'idle':
                        lock.__exit__(None,None,None)
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
    #cycle timed-out, or errored out
    return None


def sendDocument(document_path, bot_name=None):
    if os.path.exists(document_path) is False:
        return f"File {document_path} does not exist."
    size = os.path.getsize(document_path)
    if size > FILE_LIMIT_SIZE:
        return f"File too large {size} limit {FILE_LIMIT_SIZE}"
    creds_manager.select_bot(bot_name)
    document = open(document_path, 'rb')
    r = post_request("sendDocument", data={'chat_id': creds_manager.get_chat()}, files={'document': document})
    document.close()
    return r.status_code == 200


def question(prompt, bot_name=None, user_reminder = 0, max_wait=MAX_WAIT, incremental_wait=INCREMENT_WAIT, flush=False, parse_mode=None):
    global MAX_WAIT
    global MAX_RETRY
    lock_name = f"lock {creds_manager.get_select_chat()} {creds_manager.get_selected_bot()}"
    with ILock(lock_name, lock_directory=lock_directory):
        if flush:
            flush_chat()
        send_notification(prompt, bot_name=bot_name, parse_mode=parse_mode, persist=True)
        return polling(bot_name=bot_name, user_reminder = user_reminder, max_wait=max_wait, incremental_wait=incremental_wait, parse_mode=parse_mode, prompt=prompt, lock_type=None)


def get_last_offset():
    global offset
    global chats
    if len(chats) != 0 and offset != None:
        return offset
    #only necessary for the first run
    if offset is None:
        #resist network failures
        fail_counts = 0
        while True:
            r = get_request("getUpdates")
            if type(r) == str:
                time.sleep(max_wait)
                fail_counts = fail_counts + 1
                log_error(f"Get last offset failed {r}")
                if fail_counts > MAX_RETRY:
                    log_error(f"Cancelling get last offset: {f}")
                    return None
                continue
            break
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
                    #allow y and Y to solve to Yes
                    if char != char.lower():
                        short_options[char.lower()] = option

    while True:
        response = question(prompt=msg, bot_name=bot_name, user_reminder=user_reminder, parse_mode=parse_mode)
        if response in options or response in short_options:
            if response not in options:
                response = short_options[response]
            send_notification(f"{prefix_msgs} {response}.", persist=True)
            return response
        else:
            message = f'{prefix_msgs} Not an option'
            if secret == False:
                message = message + f' ({wait_for_msg})'
            send_notification(message, parse_mode=parse_mode, persist=True)


#wait for a single response, like a pause
def wait_for_user(wait_for_msg = 'K',prompt='Waiting for user to proceed', bot_name=None, prefix_msgs='Bot:', user_reminder = 180):
    flush_chat()
    wait_for_choice([wait_for_msg], prompt=prompt, bot_name=None, secret=False, prefix_msgs=prefix_msgs, user_reminder=user_reminder)


#wait for any message, like a pause
def wait_any(prompt='Waiting any input to proceed.', prefix_msgs='Bot:', bot_name=None ,done_msg=None):
    flush_chat()
    response, offset = question(prompt=prompt, bot_name=bot_name, user_reminder=0)
    if done_msg is not None and done_msg != '':
        send_notification(done_msg, persist=True)
    return response


