from aiogram import types
from aiogram.dispatcher import Dispatcher
from utils.pdf_utils import convert_pdf_to_word
from config import UPLOAD_FOLDER
import os

async def convert_start(message: types.Message):
    await message.reply("Please upload the PDF you want to convert to Word.")

async def handle_convert_file(message: types.Message):
    file_id = message.document.file_id
    file_info = await message.bot.get_file(file_id)
    file_path = os.path.join(UPLOAD_FOLDER, message.document.file_name)
    downloaded_file = await message.bot.download_file(file_info.file_path)

    with open(file_path, "wb") as f:
        f.write(downloaded_file.read())

    word_file = convert_pdf_to_word(file_path)
    await message.reply_document(open(word_file, "rb"), caption="Here is your Word file!")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(convert_start, commands=["convert_word"])
    dp.register_message_handler(handle_convert_file, content_types=["document"])
