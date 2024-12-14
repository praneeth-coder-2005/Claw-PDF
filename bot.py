import os
import tempfile

from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import PyPDF2

from config import API_ID, API_HASH, BOT_TOKEN

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_states = {}


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Image to PDF", callback_data="image_to_pdf")],
        [InlineKeyboardButton("Compress PDF", callback_data="compress_pdf")],
    ])  # Removed "Remove PDF Pages" and "Image to Telegraph" buttons
    await message.reply_text("Hello! I'm your bot. Choose an option:", reply_markup=keyboard)


@app.on_callback_query(filters.regex("image_to_pdf"))
async def image_to_pdf_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("Send me an image to convert it to PDF.")


@app.on_callback_query(filters.regex("compress_pdf"))
async def compress_pdf_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("Send me a PDF file to compress.")


@app.on_message(filters.photo)
async def handle_photo(client: Client, message: Message):
    await image_to_pdf(client, message)  # Directly call image_to_pdf


@app.on_message(filters.document)
async def handle_document(client: Client, message: Message):
    if message.document.mime_type == "application/pdf":
        await compress_pdf(client, message)  # Directly call compress_pdf
    else:
        await message.reply_text("Please send a PDF file for compression or an image for conversion to PDF.")


async def image_to_pdf(client: Client, message: Message):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            image_path = await app.download_media(message, file_name=os.path.join(tempdir, "input.jpg"))
            pdf_path = os.path.join(tempdir, "output.pdf")
            image = Image.open(image_path)
            image.save(pdf_path, "PDF", resolution=100.0)
            await message.reply_document(pdf_path, caption="Here's your PDF file.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


async def compress_pdf(client: Client, message: Message):
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            pdf_path = await app.download_media(message, file_name=os.path.join(tempdir, "input.pdf"))
            compressed_pdf_path = os.path.join(tempdir, "output.pdf")
            with open(pdf_path, "rb") as pdf_file, open(compressed_pdf_path, "wb") as compressed_pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_writer = PyPDF2.PdfWriter()
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                pdf_writer.write(compressed_pdf_file)
            await message.reply_document(compressed_pdf_path, caption="Here's your compressed PDF file.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


app.run()
            
