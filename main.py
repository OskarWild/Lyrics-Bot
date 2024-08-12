from typing import Final
from telegram import Update
from telegram.constants import ParseMode
from choirify import Choirify
import random
# await update.message.reply_text(response, parse_mode=ParseMode.HTML)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackContext, 
    ConversationHandler, filters
)

# https://replit.com/@professorfoppo/Lyrics-Bot
# https://old.uptimerobot.com/dashboard#mainDashboard

# Your bot's API token
TOKEN: Final = '7359870706:AAHyu6lFtKj9jKtPv5SxEGjNz-cvtgydB9c'
BOT_USERNAME: Final = "@NUChoirBot"

# Define the states
SELECTING_SONG, SELECTING_SHEET = range(2)

Concerts, Song_db = Choirify()

# Commands
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("""Welcome, dear choir enjoyer!
/start - Helpful commands
/lyrics - Find lyrics and information
/list - List of all songs
/ship - Ships two songs together ❤️
/sheetlist - List of songs that have music sheets
/sheets - Find the music sheet""")
    return ConversationHandler.END

async def lyrics(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Which song's lyrics are you looking for? Please provide a keyword.")
    return SELECTING_SONG

async def sheets(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Which song's music sheet are you looking for? Please provide a keyword.")
    return SELECTING_SHEET

async def list_songs(update: Update, context: CallbackContext) -> None: 
    response = "<i>Here is the list of songs and concerts:</i>\n"
    for concert in Concerts:
        response += f"\n<b>{concert}:</b>\n"
        for song in Song_db.get(concert, []):
            response += f" - {song.name}\n"
    
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

async def list_sheets(update: Update, context: CallbackContext) -> None:
    response = "<b>Here are all the songs with sheets:</b>\n\n"
    res = set()
    for concert in Concerts:
        for song in Song_db.get(concert, []):
            if song.sheets:
                res.add(song.name)
    
    for name in res:
        response += f" - {name}\n"
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

async def select_song(update: Update, context: CallbackContext) -> int:
    song_keyword = update.message.text.lower()
    
    matched_songs = []
    for concert, songs in Song_db.items():
        for song in songs:
            if song_keyword in song.name.lower():
                response = ""
                if song.lyrics:
                    response += f"ㅤㅤㅤㅤㅤㅤ<b>{song.name}</b>\n\n{song.lyrics}\n"
                elif song.images:
                    for index, image_path in enumerate(song.images):
                        with open(image_path, 'rb') as photo:
                            if index + 1== len(song.images): await update.message.reply_photo(photo=photo, caption=song.name)
                            else: await update.message.reply_photo(photo=photo)
                else:
                    await update.message.reply_text("We don't have lyrics for this song yet :(")
                if concert:
                    response += f"\n<i>This song comes from the <b>{concert}</b> concert!</i>"
                await update.message.reply_text(response, parse_mode=ParseMode.HTML)

                for i, l in enumerate(song.link):
                    if i == 0: await update.message.reply_text(f"Listen to the song here\n{l}")
                    else: await update.message.reply_text(f"{l}")
                
                if song.youtube:
                    await update.message.reply_text(f"See our performance on YouTube\n{song.youtube}")
                return ConversationHandler.END

    await update.message.reply_text("No matching songs found. Please try again.")
    return SELECTING_SONG

async def select_sheet(update: Update, context: CallbackContext) -> int:
    song_keyword = update.message.text.lower()

    for concert, songs in Song_db.items():
        for song in songs:
            if song_keyword in song.name.lower():
                if song.sheets:
                    with open(song.sheets, 'rb') as pdf_file:
                        await update.message.reply_document(document=pdf_file, caption=f"<b>{song.name}</b>",  parse_mode=ParseMode.HTML)
                else:
                    await update.message.reply_text("We don't have music sheets for this song yet :(")

                for i, l in enumerate(song.link):
                    if i == 0: await update.message.reply_text(f"Listen to the song here\n{l}")
                    else: await update.message.reply_text(f"{l}")

                return ConversationHandler.END
            
    await update.message.reply_text("No matching songs found. Please try another keyword.")
    return ConversationHandler.END

async def ship_songs(update: Update, context: CallbackContext) -> int:
    print("shipping...")
    response = "<b>Couple of the day:</b>\n"
    res = set()
    for concert in Concerts:
        for song in Song_db.get(concert, []):
            res.add(song)
    
    res_list = list(res)
    song1, song2 = random.sample(res_list, 2)

    # response += f'<a href="{song1.link[0]}">{song1.name}</a> + <a href="{song2.link[0]}">{song2.name}</a> = ❤️\nNew couple of the day may be chosen in 15 hours 22 minutes 55 seconds'
    response += f'<code><a href="{song1.link[0]}">{song1.name}</a></code> + <code><a href="{song2.link[0]}">{song2.name}</a></code> = ❤️\nNew couple of the day may be chosen in 15 hours 22 minutes 55 seconds'

    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

    await update.message.reply_text(song1.link[0])
    await update.message.reply_text(song2.link[0])
    
async def handle_message(update: Update, context: CallbackContext):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print('Bot:', response)
    await update.message.reply_text(response)

def handle_response(text: str) -> str:
    processed: str = text.lower()
    return 'Text a command! See them here - /start'

async def error(update: Update, context: CallbackContext):
    print(f'Update {update} caused error {context.error}')

def main() -> None:
    print('Starting...')
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Create the conversation handler
    conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('lyrics', lyrics), CommandHandler('sheets', sheets)],
    states={
        SELECTING_SONG: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_song)],
        SELECTING_SHEET: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_sheet)],
    },
    fallbacks=[CommandHandler('start', start), CommandHandler('list', list_songs)]
    )

    # Register handlers
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_songs))
    application.add_handler(CommandHandler("sheetlist", list_sheets))
    application.add_handler(CommandHandler("ship", ship_songs))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)

    # Start the Bot
    print('Polling...')
    application.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()
