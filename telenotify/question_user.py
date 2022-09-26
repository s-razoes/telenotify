from telenotify import user_interaction

def question(argument,bot_name=None):
    return user_interaction.question(prompt=argument,bot_name=bot_name, flush=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print('Question for user is mandatory.')
        exit(1)
    argument = sys.argv[1]
    bot_name=None
    if len(sys.argv) == 3:
        bot_name = sys.argv[2]
    response = question(argument,bot_name)
    print(response)
    exit(0)