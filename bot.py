from pyrogram import Client, filters
from pyrogram.types import Message

from config import API_ID, API_HASH, BOT_TOKEN

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("Hello! I'm your bot.")

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text("Available commands:\n/start - Start the bot\n/help - Show this help message")

@app.on_message(filters.text & ~filters.command)
async def echo(client: Client, message: Message):
    await message.reply_text(message.text)

app.run()
