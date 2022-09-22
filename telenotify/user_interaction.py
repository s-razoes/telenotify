import time
import requests

from telenotify import telegram_bots

MAX_WAIT = 60
INCREMENT_WAIT = 1


def send_notification(message, bot_name=None):
    telegram_bots.select_bot(bot_name)
    r = requests.get(f"https://api.telegram.org/bot{telegram_bots.get_token()}/sendMessage?chat_id={telegram_bots.get_chat()}&text={message}")


def polling(bot_name=None, user_reminder = 0, offset=None, max_wait=MAX_WAIT, incremental_wait=INCREMENT_WAIT):
    telegram_bots.select_bot(bot_name)
    if offset is None:
        offset = get_last_offset()
    start_wait = 5
    wait_interval = start_wait
    cycle = 0
    while True:
        body = {"offset": offset}
        r = requests.post(f"https://api.telegram.org/bot{telegram_bots.get_token()}/getUpdates",data=body)

        if r.status_code == 200:
            results = r.json()['result']
            for result in results:
                if result['update_id'] > int(offset):
                    wait_interval = start_wait
                    cycle = 0
                    offset = result['update_id']
                    if 'message' in result:
                        if result['message']['from']['username'] == telegram_bots.get_auth_user():
                            return result['message']['text'], offset
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
    requests.post(F"https://api.telegram.org/bot{telegram_bots.get_token()}/sendDocument", data={'chat_id': telegram_bots.get_chat()}, files={'document': document})
    document.close()



def question(prompt, bot_name=None, user_reminder = 0, offset=None, max_wait=MAX_WAIT, incremental_wait=INCREMENT_WAIT):
    send_notification(prompt, bot_name)    
    return polling(bot_name=bot_name, user_reminder = user_reminder, offset=offset, max_wait=max_wait, incremental_wait=incremental_wait)


def get_last_offset():
    r = requests.get(F"https://api.telegram.org/bot{telegram_bots.get_token()}/getUpdates")
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

    offset = None
    while True:
        response, offset = question(prompt=msg, bot_name=bot_name, user_reminder=user_reminder, offset=offset)
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

