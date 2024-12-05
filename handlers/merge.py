from aiogram import types
from aiogram.dispatcher import Dispatcher
from utils.pdf_utils import merge_pdfs
from config import UPLOAD_FOLDER
import os

user_data = {}  # Store user session data

async def merge_start(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"action": "merge", "files": []}
    await message.reply("Please upload the PDFs you want to merge. Type /done when finished.")

async def handle_file_upload(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in user_data or user_data[chat_id]["action"] != "merge":
        await message.reply("Please start with /merge before uploading files.")
        return

    # Save uploaded file
    file_id = message.document.file_id
    file_info = await message.bot.get_file(file_id)
    file_path = os.path.join(UPLOAD_FOLDER, message.document.file_name)
    downloaded_file = await message.bot.download_file(file_info.file_path)

    with open(file_path, "wb") as f:
        f.write(downloaded_file.read())

    user_data[chat_id]["files"].append(file_path)
    await message.reply(f"Added {message.document.file_name}. Type /done when finished.")

async def merge_done(message: types.Message):
    chat_id = message.chat.id
    files = user_data.get(chat_id, {}).get("files", [])
    if len(files) < 2:
        await message.reply("Please upload at least two PDFs to merge.")
        return

    output_file = os.path.join(UPLOAD_FOLDER, f"merged_{chat_id}.pdf")
    merge_pdfs(files, output_file)

    await message.reply_document(open(output_file, "rb"), caption="Here is your merged PDF!")
    user_data.pop(chat_id)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(merge_start, commands=["merge"])
    dp.register_message_handler(handle_file_upload, content_types=["document"])
    dp.register_message_handler(merge_done, commands=["done"])
