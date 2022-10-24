![Version 1](http://img.shields.io/badge/version-v1.55-green.svg)
![Python 3.8](http://img.shields.io/badge/python-3.8-blue.svg)
[![MIT License](http://img.shields.io/badge/license-MIT%20License-blue.svg)](https://github.com/s-razoes/updog/blob/master/LICENSE)


telenotify is a simple telegram, none webhook interaction python module.

## Installation

Install using pip:

`pip3 install git+https://github.com/s-razoes/telenotify`

Afterward don't forget to add the **TOKEN** and **CHAT_ID** to your **bots_creds.json**


## Location of creds.json

Run:

`pip3 show telenotify|grep Location`

That should return the directory where it was installed, in it the telenotify directory should contain the **bots_creds.json**

## Usage from bash

BOT_NAME is optional will define which bot the notifications will come, if not present will use the default, most cases shouldn't be needing it.

Send notification to user from bash

`telenotify BOT_NAME Message`

Ask user a question and wait for reply

`python3 -m telenotify.question_user BOT_NAME QUESTION`

Send broadcast message to all users in the configuration

`python3 -m telenotify.broadcast BOT_NAME MESSAGE`