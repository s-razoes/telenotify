import argparse
from telenotify.telegram_bots import creds_manager


def main():
    parser = argparse.ArgumentParser(description='Telegram bots credential manager.') 
    parser.add_argument('-ab', required=False, help="add bot")
    parser.add_argument('-rb', required=False, help="remove bot")
    parser.add_argument('-db', required=False, help="defines the bot as default")
    parser.add_argument('-au', required=False, help="add user")
    parser.add_argument('-ru', required=False, help="remove user")
    parser.add_argument('-du', required=False, help="default user")
    parser.add_argument('-su', required=False, help="set authenticated user")
    parser.add_argument('-t', required=False, help="token for adding user or bot")
    args = parser.parse_args()

    #add bot/user must have token
    if args.t is None:
        if args.ab is not None or args.au is not None:
            print("Token must be provided for this option")
            quit()
    #confusion option
    if args.t is not None:
        if args.rb is not None or args.ru is not None or args.db is not None or args.du is not None or args.su is not None:
            print("Token is not need. I'm confused here.")
            quit()
    
    #verify it is only one option at a time
    count = 0
    for key, value in vars(args).items():
        if key != 't' and value is not None:
            count = count + 1
    if count > 1:
        print("Wrong usage!")
        quit()

    if count == 0:
        parser.print_help()
        print('===Credentials===')
        creds_manager.print_info()
        quit()

    if args.ab is not None:
        creds_manager.add_bot(args.ab, args.t)
        print("bot added")
    if args.rb is not None:
        creds_manager.del_bot(args.rb)
        print("bot removed")
    if args.db is not None:
        creds_manager.set_default_bot(args.db)
        print("bot set as default")
    if args.au is not None:
        creds_manager.add_user(args.au, args.t)
        print("user added")
    if args.ru is not None:
        creds_manager.del_user(args.ru)
        print("user removed")
    if args.du is not None:
        creds_manager.set_default_user(args.du)
        print("user set as default")
    if args.su is not None:
        creds_manager.set_auth_user(args.su)
        print("user set as the authenticated user")

if __name__ == "__main__":
    main()
