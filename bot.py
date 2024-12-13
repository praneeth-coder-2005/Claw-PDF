import os
import tempfile

from pdf2image import convert_from_path
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message

from config import API_ID, API_HASH, BOT_TOKEN

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("Hello! I'm your bot. Send me an image to convert it to PDF.")

@app.on_message(filters.photo)
async def image_to_pdf(client: Client, message: Message):
    try:
        # Download the image
        with tempfile.TemporaryDirectory() as tempdir:
            image_path = await app.download_media(message, file_name=os.path.join(tempdir, "input.jpg"))

            # Convert image to PDF
            pdf_path = os.path.join(tempdir, "output.pdf")
            image = Image.open(image_path)
            image.save(pdf_path, "PDF", resolution=100.0)

            # Send the PDF
            await message.reply_document(pdf_path, caption="Here's your PDF file.")

    except Exception as e:
        await message.reply_text(f"Error: {e}")

app.run()
