# bot.py

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handlers import register_all_handlers

def main():
    # Initialize the bot with your API token
    updater = Updater("YOUR_BOT_API_TOKEN", use_context=True)
    dispatcher = updater.dispatcher
    
    # Register all handlers (including the one for PDF to Word conversion)
    register_all_handlers(dispatcher)
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
