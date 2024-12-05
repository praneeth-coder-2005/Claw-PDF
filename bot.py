# bot.py

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from handlers import register_all_handlers  # Assuming you will use aiogram's handler structure

API_TOKEN = 'YOUR_BOT_API_TOKEN'  # Replace with your Telegram bot token

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Register handlers (we'll assume 'register_all_handlers' is adjusted for aiogram)
register_all_handlers(dp)

async def on_start(message: types.Message):
    await message.reply("Hello! I am your PDF-to-Word bot!")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
