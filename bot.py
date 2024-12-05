# bot.py

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from handlers import register_all_handlers  # Assuming you will use aiogram's handler structure

API_TOKEN = 'YOUR_BOT_API_TOKEN'  # Replace with your Telegram bot token

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Register handlers
register_all_handlers(dp)

async def on_start(message: types.Message):
    await message.reply("Hello! I am your PDF-to-Word bot!")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
