from telenotify import user_interaction

def broadcast(message,bot_name):
    send_broadcast(message,bot_name=bot_name)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print(f'Message to broadcast is mandatory.\nUsage: {sys.argv[0]} BOT_NAME MESSAGE\nOr for default bot: {sys.argv[0]} MESSAGE')
        exit(1)
    
    bot_name=None
    if len(sys.argv) == 3:
        bot_name = sys.argv[1]
        argument = sys.argv[2]
    else:
        argument = sys.argv[1]
    response = broadcast(argument,bot_name)
    print(response)
    exit(0)