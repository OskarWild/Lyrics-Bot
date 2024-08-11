from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')

app = Flask(__name__)
bot = Bot(TOKEN)
application = Application.builder().token(TOKEN).build()

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    application.process_update(update)
    return 'OK', 200

@app.route('/')
def index():
    return 'Bot is running!'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)