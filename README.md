![Version 1](http://img.shields.io/badge/version-v1.13-green.svg)
![Python 3.8](http://img.shields.io/badge/python-3.8-blue.svg)
[![MIT License](http://img.shields.io/badge/license-MIT%20License-blue.svg)](https://github.com/s-razoes/updog/blob/master/LICENSE)


telenotify is a simple telegram, no webhook, user interaction python module and simple for being used from the command line.

## Installation

Install using pip:

`pip3 install git+https://github.com/s-razoes/telenotify`

Afterward don't forget to add the **TOKEN** and **CHAT_ID** to your configuration


## Adding credentials and chats

Run:

`python3 -m telenotify.telegram_bots`

That should return the current status of your credentials.

After install should be empty.

You should have at least one chat and one bot for it to function properly.

To add your bot and token:

`python3 -m telenotify.telegram_bots -ab #BOT_NAME# -t #TOKEN#`

To add a user:

`python3 -m telenotify.telegram_bots -au #USER_NICKNAME# -t #CHAT_ID#`

These will be used system wide and no further configuration should be necessary.

## Usage from bash

BOT_NAME is optional will define which bot the notifications will come, if not present will use the default.
NICKNAME is optional will define which user will receive the message/file.

Send notification to user from bash:

`telenotify #BOT_NAME# #NICKNAME# Message`

Ask user a question and wait for reply:

`telequestion #BOT_NAME# #NICKNAME# QUESTION`

Send broadcast message to all users in the configuration:

`telebroad #BOT_NAME# MESSAGE`

Send broadcast message to all users in the configuration:

`telefile #BOT_NAME# #NICKNAME# FILE_PATH`

![screenshot](https://raw.githubusercontent.com/s-razoes/telenotify/master/example_question.png)