from flask import Flask, request
import telegram
from telebot.credentials import bot_token, bot_user_name, URL
import requests

global bot
global TOKEN
global bot_token
global bot_user_name
global URL 
bot_token = "Your Bot API token"
bot_user_name = "gci_fedora_bot"
URL = "Link for your hosted app"
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)


app = Flask(__name__)

DATA_URL = "https://api.github.com/orgs/fedora-infra/repos"


def get_data():
    return requests.get(DATA_URL).json()


def get_repo_count():
    data = get_data()
    return len(data)


def get_repo_names():
    Names = []
    data = get_data()
    for repo in data:
        Names += [repo['name']]
    return list(zip(list(range(1, len(data)+1)), Names))


def get_fork_count(index):
    return get_data()[index-1]['forks']


@app.route('/{}'.format(TOKEN), methods=["POST"])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat_id
    msg_id = update.message.message_id

    text = update.message.text.encode('utf-8').decode()

    print("Recieved Text Message: ", text)

    bot_welcome = """
            Welcome to gci_fedora_bot.
            /help for help message
            /repos for the name of all the repos
            /repo_count for the number of repos
            /fork_count <repo_index> returns the count of the forks for that particular repo, index is the one you get from /repos.
        """
    if text == "/start":
        bot.sendMessage(chat_id=chat_id, text=bot_welcome,
                        reply_to_message_id=msg_id)
    else:
        if "/help" in text:
            message = bot_welcome
        elif "/repos" in text:
            Names = get_repo_names()
            message = ""
            for name in Names:
                message += f'{name[0]}. {name[1]}\n'
        elif "/repo_count" in text:
            message = get_repo_count()

        elif '/fork_count' in text:
            message = text.split()[1]
            try:
                message = get_fork_count(int(message))
            except:
                message = "Invalid Index."

        else:
            message = "Invalid Choice."

        bot.sendMessage(chat_id=chat_id, text=message,
                        reply_to_message_id=msg_id)

    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route("/")
def index():
    return '.'


if __name__ == "__main__":
    app.run(threaded=True)
