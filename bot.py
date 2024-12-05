from aiogram import Bot, Dispatcher, executor, types
import os
from PyPDF2 import PdfMerger
import fitz  # PyMuPDF

# Environment variables for secure deployment
API_TOKEN = os.getenv("API_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# User session data (in-memory)
user_data = {}

# Start command
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply(
        "Welcome to the PDF Bot!\n"
        "Available commands:\n"
        "/merge - Merge multiple PDFs\n"
        "/compress - Compress a PDF\n"
        "/convert_word - Convert PDF to Word\n"
        "/done - Finish the current operation"
    )

# Handle /merge command
@dp.message_handler(commands=["merge"])
async def merge_handler(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"action": "merge", "files": []}
    await message.reply("Please upload the PDFs you want to merge. Type /done when finished.")

# Handle /compress command
@dp.message_handler(commands=["compress"])
async def compress_handler(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"action": "compress"}
    await message.reply("Please upload the PDF you want to compress.")

# Handle /convert_word command
@dp.message_handler(commands=["convert_word"])
async def convert_word_handler(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = {"action": "convert_word"}
    await message.reply("Please upload the PDF you want to convert to Word.")

# Handle file uploads
@dp.message_handler(content_types=["document"])
async def handle_file_upload(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        await message.reply("Please start an operation first using one of the commands like /merge, /compress, or /convert_word.")
        return

    # Save the uploaded file
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = os.path.join(UPLOAD_FOLDER, message.document.file_name)
    downloaded_file = await bot.download_file(file_info.file_path)

    with open(file_path, "wb") as f:
        f.write(downloaded_file.read())

    # Handle based on the user's current action
    action = user_data[chat_id]["action"]

    if action == "merge":
        user_data[chat_id]["files"].append(file_path)
        await message.reply(f"Added {message.document.file_name}. Type /done when finished.")
    elif action == "compress":
        compressed_file = compress_pdf(file_path)
        await message.reply_document(open(compressed_file, "rb"), caption="Here is your compressed PDF!")
        user_data.pop(chat_id)
    elif action == "convert_word":
        word_file = convert_pdf_to_word(file_path)
        await message.reply_document(open(word_file, "rb"), caption="Here is your Word file!")
        user_data.pop(chat_id)

# Handle /done command for merging
@dp.message_handler(commands=["done"])
async def done_handler(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in user_data or user_data[chat_id]["action"] != "merge":
        await message.reply("You have no active operation. Use /merge to start merging PDFs.")
        return

    # Merge the PDFs
    files = user_data[chat_id]["files"]
    if len(files) < 2:
        await message.reply("Please upload at least two PDFs to merge.")
        return

    output_file = os.path.join(UPLOAD_FOLDER, f"merged_{chat_id}.pdf")
    merge_pdfs(files, output_file)

    await message.reply_document(open(output_file, "rb"), caption="Here is your merged PDF!")
    user_data.pop(chat_id)

# Merge PDFs function
def merge_pdfs(files, output_file):
    merger = PdfMerger()
    for pdf in files:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()

# Compress PDF function
def compress_pdf(input_file):
    output_file = input_file.replace(".pdf", "_compressed.pdf")
    doc = fitz.open(input_file)
    doc.save(output_file, deflate=True)
    doc.close()
    return output_file

# Convert PDF to Word function
def convert_pdf_to_word(input_file):
    from pdf2docx import Converter
    output_file = input_file.replace(".pdf", ".docx")
    cv = Converter(input_file)
    cv.convert(output_file, start=0, end=None)
    cv.close()
    return output_file

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
