from aiogram import types
from aiogram.dispatcher import Dispatcher
from utils.pdf_utils import compress_pdf
from config import UPLOAD_FOLDER
import os

async def compress_start(message: types.Message):
    await message.reply("Please upload the PDF you want to compress.")

async def handle_compress_file(message: types.Message):
    file_id = message.document.file_id
    file_info = await message.bot.get_file(file_id)
    file_path = os.path.join(UPLOAD_FOLDER, message.document.file_name)
    downloaded_file = await message.bot.download_file(file_info.file_path)

    with open(file_path, "wb") as f:
        f.write(downloaded_file.read())

    compressed_file = compress_pdf(file_path)
    await message.reply_document(open(compressed_file, "rb"), caption="Here is your compressed PDF!")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(compress_start, commands=["compress"])
    dp.register_message_handler(handle_compress_file, content_types=["document"])
