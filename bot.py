from aiogram import Bot, Dispatcher, executor, types
import os
from config import API_TOKEN
from handlers import merge, compress, convert  # Import feature handlers

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Start command
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply(
        "Welcome to the PDF Bot! Available commands:\n"
        "/merge - Merge multiple PDFs\n"
        "/compress - Compress a PDF\n"
        "/convert_word - Convert PDF to Word\n"
        "/done - Finish the current operation"
    )

# Feature routes
merge.register_handlers(dp)
compress.register_handlers(dp)
convert.register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
