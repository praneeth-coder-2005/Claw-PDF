import os
import tempfile

from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import PyPDF2
from telegraph import upload_file

from config import API_ID, API_HASH, BOT_TOKEN

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_states = {}


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Image to PDF", callback_data="image_to_pdf")],
        [InlineKeyboardButton("Compress PDF", callback_data="compress_pdf")],
        [InlineKeyboardButton("Remove PDF Pages", callback_data="remove_pdf_pages")],
        [InlineKeyboardButton("Image to Telegraph", callback_data="image_to_telegraph")]
    ])
    await message.reply_text("Hello! I'm your bot. Choose an option:", reply_markup=keyboard)


@app.on_callback_query(filters.regex("image_to_pdf"))
async def image_to_pdf_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("Send me an image to convert it to PDF.")


@app.on_callback_query(filters.regex("compress_pdf"))
async def compress_pdf_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("Send me a PDF file to compress.")


@app.on_callback_query(filters.regex("remove_pdf_pages"))
async def remove_pdf_pages_callback(client: Client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    user_states[user_id] = "waiting_for_pdf"
    await callback_query.message.reply_text("Please send me the PDF file from which you want to remove pages.")


@app.on_callback_query(filters.regex("image_to_telegraph"))
async def image_to_telegraph_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("Send me an image to upload to Telegraph.")


@app.on_message(filters.photo)
async def handle_photo(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == "waiting_for_pdf":
        await handle_pdf_for_page_removal(client, message)
    else:
        await image_to_telegraph(client, message)


@app.on_message(filters.document)
async def handle_document(client: Client, message: Message):
    if message.document.mime_type == "application/pdf":
        user_id = message.from_user.id
        if user_id in user_states and user_states[user_id] == "waiting_for_pdf":
            await handle_pdf_for_page_removal(client, message)
        else:
            await compress_pdf(client, message)
    else:
        await message.reply_text("Please send a PDF file for compression or an image for uploading to Telegraph.")


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


@app.on_message(filters.text)
async def handle_page_numbers(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and isinstance(user_states[user_id], dict) and \
       user_states[user_id]["state"] == "waiting_for_page_numbers":
        try:
            pdf_path = user_states[user_id]["pdf_path"]
            page_numbers_str = message.text.strip()
            page_numbers_to_remove = []
            try:
                for part in page_numbers_str.split(","):
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        page_numbers_to_remove.extend(range(start, end + 1))
                    else:
                        page_numbers_to_remove.append(int(part))
            except ValueError:
                await message.reply_text("Invalid page numbers format.")
                return

            output_pdf_path = os.path.join(tempfile.gettempdir(), "output.pdf")
            with open(pdf_path, "rb") as pdf_file, open(output_pdf_path, "wb") as output_pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_writer = PyPDF2.PdfWriter()
                for page_num in range(len(pdf_reader.pages)):
                    if page_num + 1 not in page_numbers_to_remove:
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                pdf_writer.write(output_pdf_file)

            await message.reply_document(output_pdf_path, caption="Here's your PDF with pages removed.")

        except Exception as e:
            await message.reply_text(f"Error: {e}")
        finally:
            del user_states[user_id]


async def image_to_telegraph(client: Client, message: Message):
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            await app.download_media(message, file_name=temp_file.name)
            response = upload_file(temp_file.name)
            
            # Check if the response is a list and has at least one element
            if isinstance(response, list) and len(response) > 0:  
                image_url = "https://telegra.ph" + response[0]
                await message.reply_text(f"Here's your Telegraph image URL: {image_url}")
            else:
                await message.reply_text("Error uploading image to Telegraph. Please try again later.")

    except Exception as e:
        await message.reply_text(f"Error: {e}")
    finally:
        os.remove(temp_file.name)

app.run()
                
