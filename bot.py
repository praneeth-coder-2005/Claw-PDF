from aiogram import Bot, Dispatcher, executor, types
import os

# Load environment variables
API_TOKEN = os.getenv("API_TOKEN")  # Set this in Render Environment
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/uploads")  # Default to /tmp/uploads for Render

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Start command handler
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Welcome to the PDF Bot! Choose a feature using commands.")

# Example command for testing
@dp.message_handler(commands=["test"])
async def test_command(message: types.Message):
    await message.reply("Your bot is up and running!")

if __name__ == "__main__":
    print("Starting bot...")
    executor.start_polling(dp, skip_updates=True)
