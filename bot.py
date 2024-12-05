from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN  # Import bot token
from handlers import register_all_handlers  # Register all feature handlers

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Start command
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply(
        "Welcome to the PDF Bot! Here are the available commands:\n"
        "/merge - Merge multiple PDFs\n"
        "/compress - Compress a PDF\n"
        "/convert_word - Convert PDF to Word\n"
        "/done - Finish the current operation"
    )

# Register all feature handlers
register_all_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
