import sys
from telenotify import user_interaction

def broadcast(message,bot_name):
    user_interaction.send_broadcast(message,bot_name=bot_name)

def main():
    if len(sys.argv) == 1:
        print(f'Message to broadcast is mandatory.')
        print(f'Usage: {sys.argv[0]} BOT_NAME MESSAGE')
        print(f'Or for default bot: {sys.argv[0]} MESSAGE')
        exit(1)
    
    bot_name=None
    if len(sys.argv) == 3:
        bot_name = sys.argv[1]
        argument = sys.argv[2]
    else:
        argument = sys.argv[1]
    broadcast(argument,bot_name)
    exit(0)


if __name__ == "__main__":
    main()