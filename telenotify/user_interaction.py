import time
import requests
from datetime import datetime
import urllib.parse

from telenotify import telegram_bots

MAX_RETRY = 10
MAX_WAIT = 60
INCREMENT_WAIT = 1
offset = None

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


def send_notification(message, bot_name=None):
    message = urllib.parse.quote(message.strip())
    telegram_bots.select_bot(bot_name)
    return get_request("sendMessage",f"chat_id={telegram_bots.get_chat()}&text={message}")


def polling(bot_name=None, user_reminder = 0, max_wait=MAX_WAIT, incremental_wait=INCREMENT_WAIT):
    global offset
    global MAX_RETRY
    telegram_bots.select_bot(bot_name)
    offset = get_last_offset()
    start_wait = 5
    wait_interval = start_wait
    cycle = 0
    fail_counts = 0
    while True:
        r = post_request("getUpdates",data={"offset": offset})
        
        if type(r) == str:
            #exception occurred
            log_error(f"Exception:{r}")
            wait_interval = max_wait
            fail_counts = fail_counts + 1
            if fail_counts > MAX_RETRY:
                log_error("Cancelling polling")
                return None
        else:
            if r.status_code == 200:
                fail_counts = 0
                results = r.json()['result']
                for result in results:
                    if result['update_id'] > int(offset):
                        wait_interval = start_wait
                        cycle = 0
                        offset = result['update_id']
                        #stickers, emoji, etc
                        if 'message' not in result or 'text' not in result['message']:
                            log_error(f"Message missing from response:{result}")
                            continue
                        if result['message']['from']['username'] == telegram_bots.get_auth_user():
                            return result['message']['text']
            else:
                #error
                log_error(f"HTTP error:{r.status_code}")
                wait_interval = max_wait
                fail_counts = fail_counts + 1
                if fail_counts > MAX_RETRY:
                    log_error("Cancelling polling")
                    return None
        time.sleep(wait_interval)
        if wait_interval < max_wait:
            wait_interval = cycle * incremental_wait
            if wait_interval > max_wait:
                wait_interval = max_wait
        cycle = cycle + 1

        if user_reminder > 0:
            if cycle%user_reminder == 0:
                send_notification(prompt)

def sendDocument(document_path):
    document = open(document_path, 'rb')
    r = post_request("sendDocument", data={'chat_id': telegram_bots.get_chat()}, files={'document': document})
    document.close()
    return r


def question(prompt, bot_name=None, user_reminder = 0, max_wait=MAX_WAIT, incremental_wait=INCREMENT_WAIT):
    global MAX_WAIT
    global MAX_RETRY
    try_count = 0
    while True:
        try_count = try_count + 1
        r = send_notification(prompt, bot_name)
        if type(r) == str:
            log_error(f"Failure asking:{prompt}\n{r}")
            if MAX_RETRY > try_count:
                raise Exception("Exceeded tries")
            time.sleep(MAX_WAIT)
            continue
        return polling(bot_name=bot_name, user_reminder = user_reminder, max_wait=max_wait, incremental_wait=incremental_wait)


def get_last_offset():
    global offset
    #only necessary for the first run
    if offset is None:
        r = get_request("getUpdates")
        results = r.json()['result']
        offset = 0
        if len(results) > 0:
            for result in results:
                offset = result['update_id']
    return offset


#will wait for a response from the user and return the string of that choice
def wait_for_choice(options, prompt="waiting for user's choice", bot_name=None, secret=False, prefix_msgs='Choice:', user_reminder = 0):
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
        response = question(prompt=msg, bot_name=bot_name, user_reminder=user_reminder)
        if response in options or response in short_options:
            if response not in options:
                response = short_options[response]
            send_notification(f"{prefix_msgs} {response}.")
            return response
        else:
            message = f'{prefix_msgs} Not an option'
            if secret == False:
                message = message + f' ({wait_for_msg})'
            send_notification(message)


#wait for a single response, like a pause
def wait_for_user(wait_for_msg = 'K',prompt='Waiting for user to proceed', bot_name=None, prefix_msgs='Bot:', user_reminder = 180):
    wait_for_choice([wait_for_msg], prompt=prompt, bot_name=None, secret=False, prefix_msgs=prefix_msgs, user_reminder=user_reminder)


#wait for any message, like a pause
def wait_any(prompt='Waiting any input to proceed.', prefix_msgs='Bot:', bot_name=None ,done_msg=None):
    response, offset = question(prompt=prompt, bot_name=bot_name, user_reminder=0)
    if done_msg is not None and done_msg != '':
        send_notification(done_msg)
    return response

