![Version 1](http://img.shields.io/badge/version-v1.13-green.svg)
![Python 3.8](http://img.shields.io/badge/python-3.8-blue.svg)
[![MIT License](http://img.shields.io/badge/license-MIT%20License-blue.svg)](https://github.com/s-razoes/updog/blob/master/LICENSE)


**telenotify** is a simple telegram, no webhook, user interaction python module able to be used from the command line or scripts globaly within the system.

# Installation

Install using pip:

```bash
pip3 install git+https://github.com/s-razoes/telenotify`
```

Afterward don't forget to add the credentials, these will be used system wide and no further configuration should be necessary.

## Adding credentials and chats

After install and creating a bot you'll need to add the tokens and chats using these commands.

### Add bot or replace the token:

```bash
python3 -m telenotify.telegram_bots -ab BOT_NAME -t TOKEN
```

The bot name is the one being called from the scripts

### Set bot as default, if there's only one, this is uncessary:

```bash
python3 -m telenotify.telegram_bots -db BOT_NAME
```

### Add chat (aka user):

```bash
python3 -m telenotify.telegram_bots -au USER_NAME -t CHAT_ID
```

### Set user as authenticated user, if there's only one this step is uncessary:

```bash
python3 -m telenotify.telegram_bots -su USER_NAME
```

### Set user as default, if there's only one this step is uncessary:

```bash
python3 -m telenotify.telegram_bots -du USER_NAME
```

# Usage from bash

**BOT_NAME** is optional will define which bot the notifications will come, if not present will use the default.

**USER_NAME** is optional will define which user will receive the message/file.

Send notification to user from bash:

```bash
telenotify BOT_NAME USER_NAME Message
```

Ask user a question and wait for reply:

```bash
telequestion BOT_NAME USER_NAME Question
```

Send broadcast message to all users in the configuration:

```bash
telebroad BOT_NAME Message
```

Send file from system to user:

```bash
telefile BOT_NAME USER_NAME FILE_PATH
```

![screenshot](https://raw.githubusercontent.com/s-razoes/telenotify/master/example_question.png)

# Usage from python scripts

The BOT_NAME and USER_NAME are optional, if none are set, the defaults will be used.

### Import:

```python
from telenotify import user_interaction
```

### Simple notification:

```python
user_interaction.send_notification('hey!', 'BOT_NAME',nickname='USER_NAME')
```

### Broadcast message to all chats:

```python
user_interaction.send_broadcast('Major anouncement', 'BOT_NAME')
```

### Ask user input:

```python
response = user_interaction.question('How are you?',bot_name='BOT_NAME', nickname='USER_NAME')
```

### Choice for the authenticated user:

```python
choice = user_interaction.wait_for_choice(options=['Ok','Cancel'],bot_name='BOT_NAME',prompt="There was an error should I continue?")
if choice == 'Cancel':
    print('User cancelled')
if choice == 'Ok':
    print('User confirmed')
```

### Send file:
```python
user_interaction.send_document(FILE_PATH, 'BOT_NAME',nickname='USER_NAME')
```


## To create a bot:

https://learn.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram