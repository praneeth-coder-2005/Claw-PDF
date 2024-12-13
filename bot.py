import os
import tempfile

from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import PyPDF2

from config import API_ID, API_HASH, BOT_TOKEN

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store user states
user_states = {}


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Image to PDF", callback_data="image_to_pdf")],
        [InlineKeyboardButton("Compress PDF", callback_data="compress_pdf")],
        [InlineKeyboardButton("Remove PDF Pages",
                              callback_data="remove_pdf_pages")]
    ])
    await message.reply_text("Hello! I'm your bot. Choose an option:",
                            reply_markup=keyboard)


@app.on_callback_query(filters.regex("image_to_pdf"))
async def image_to_pdf_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("Send me an image to convert it to PDF.")


@app.on_message(filters.photo)
async def image_to_pdf(client: Client, message: Message):
    try:
        # Download the image
        with tempfile.TemporaryDirectory() as tempdir:
            image_path = await app.download_media(
                message, file_name=os.path.join(tempdir, "input.jpg"))

            # Convert image to PDF
            pdf_path = os.path.join(tempdir, "output.pdf")
            image = Image.open(image_path)
            image.save(pdf_path, "PDF", resolution=100.0)

            # Send the PDF
            await message.reply_document(pdf_path,
                                        caption="Here's your PDF file.")

    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_callback_query(filters.regex("compress_pdf"))
async def compress_pdf_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text("Send me a PDF file to compress.")


@app.on_message(filters.document)
async def compress_pdf(client: Client, message: Message):
    if message.document.mime_type == "application/pdf":
        try:
            # Download the PDF
            with tempfile.TemporaryDirectory() as tempdir:
                pdf_path = await app.download_media(
                    message, file_name=os.path.join(tempdir, "input.pdf"))

                # Compress the PDF
                compressed_pdf_path = os.path.join(tempdir, "output.pdf")
                with open(pdf_path, "rb") as pdf_file, open(
                        compressed_pdf_path, "wb") as compressed_pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pdf_writer = PyPDF2.PdfWriter()

                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                    pdf_writer.write(compressed_pdf_file)

                # Send the compressed PDF
                await message.reply_document(compressed_pdf_path,
                                            caption="Here's your compressed PDF file.")

        except Exception as e:
            await message.reply_text(f"Error: {e}")
    else:
        await message.reply_text("Please send a PDF file.")


@app.on_callback_query(filters.regex("remove_pdf_pages"))
async def remove_pdf_pages_callback(client: Client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    user_states[user_id] = "waiting_for_pdf"
    await callback_query.message.reply_text(
        "Please send me the PDF file from which you want to remove pages.")


@app.on_message(filters.document)
async def handle_pdf_for_page_removal(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[
            user_id] == "waiting_for_pdf":
        if message.document.mime_type == "application/pdf":
            try:
                # Download the PDF
                with tempfile.TemporaryDirectory() as tempdir:
                    pdf_path = await app.download_media(
                        message, file_name=os.path.join(tempdir, "input.pdf"))
                    user_states[user_id] = {
                        "state": "waiting_for_page_numbers",
                        "pdf_path": pdf_path
                    }
                    await message.reply_text(
                        "Please specify the page numbers to remove (e.g., `1, 3-5, 7`)."
                    )
            except Exception as e:
                await message.reply_text(f"Error: {e}")
                del user_states[user_id]
        else:
            await message.reply_text("Please send a PDF file.")
            del user_states[user_id]


@app.on_message(filters.text)
async def handle_page_numbers(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and isinstance(user_states[user_id], dict) and \
       user_states[user_id]["state"] == "waiting_for_page_numbers":
        try:
            pdf_path = user_states[user_id]["pdf_path"]

            page_numbers_to_remove =

            page_numbers_str = message.text.strip()
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

            # Remove pages from the PDF
            output_pdf_path = os.path.join(tempfile.gettempdir(), "output.pdf")
            with open(pdf_path, "rb") as pdf_file, open(output_pdf_path,
                                                        "wb") as output_pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_writer = PyPDF2.PdfWriter()

                for page_num in range(len(pdf_reader.pages)):
                    if page_num + 1 not in page_numbers_to_remove:
                        pdf_writer.add_page(pdf_reader.pages[page_num])

                pdf_writer.write(output_pdf_file)

            # Send the modified PDF
            await message.reply_document(output_pdf_path,
                                        caption="Here's your PDF with pages removed.")

        except Exception as e:
            await message.reply_text(f"Error: {e}")
        finally:
            del user_states[user_id]


app.run()
            
