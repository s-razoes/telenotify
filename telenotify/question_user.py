import sys
from telenotify import user_interaction

def question(msg,bot_name=None,chat=None):
    return user_interaction.question(prompt=msg,bot_name=bot_name, flush=True, nickname=chat)

def main():
    if len(sys.argv) == 1:
        print(f'Question for user is mandatory.')
        print(f'Usage: {sys.argv[0]} QUESTION - using default bot')
        print(f'{sys.argv[0]} (BOT_NAME) QUESTION')
        print(f'{sys.argv[0]} (BOT_NAME) (CHAT) QUESTION')
        exit(1)
    
    bot_name=None
    chat=None
    if len(sys.argv) == 3:
        bot_name = sys.argv[1]
        msg = sys.argv[2]
    if len(sys.argv) == 2:
        msg = sys.argv[1]
    if len(sys.argv) == 4:
        bot_name = sys.argv[1]
        chat = sys.argv[2]
        msg = sys.argv[3]
    response = question(msg,bot_name,chat)
    print(response)
    exit(0)


if __name__ == "__main__":
    main()