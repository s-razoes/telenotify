import sys
from telenotify import user_interaction


def main():
    if len(sys.argv) == 1:
        print(f'Notification for user is mandatory.')
        print(f'Usage: {sys.argv[0]} message')
        print(f'{sys.argv[0]} (BOT_NAME) message')
        print(f'{sys.argv[0]} (BOT_NAME) (CHAT) message')
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
    user_interaction.send_notification(msg, bot_name, chat)
    exit(0)


if __name__ == "__main__":
    main()

       