from telenotify.user_interaction import user_interaction
import sys

if len(sys.argv) == 1:
    print('Question for user is mandatory.')
    exit(1)

argument = sys.argv[1]
bot_name=None
if len(sys.argv) == 3:
    bot_name = sys.argv[2]
response = user_interaction.question(argument,bot_name)
print(response)
exit(0)
