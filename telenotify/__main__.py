import argparse
from telenotify import user_interaction


def main():
    parser = argparse.ArgumentParser(description='Send a notification via telegram.')
    parser.add_argument('bot_name', help='If you don\'t want the default bot, name it')
    parser.add_argument('text', help='The text to send')
    args = parser.parse_args()

    if args.text == '':
        print("No text provided")
        quit(1)
    user_interaction.send_notification(args.text,args.bot_name)

if __name__ == "__main__":
    main()

       