# handlers/convert.py

from aiogram import types
from utils.pdf_utils import convert_pdf_to_word

async def handle_pdf(message: types.Message):
    # Check if the message contains a document
    if message.document and message.document.mime_type == "application/pdf":
        # Get the file ID of the uploaded PDF
        file_id = message.document.file_id
        
        # Get the file from Telegram servers
        file = await message.bot.get_file(file_id)
        pdf_path = file.file_path
        word_path = f"/path/to/word/{file.file_id}.docx"

        # Download the PDF file
        await message.bot.download_file(pdf_path, word_path)

        # Convert PDF to Word
        convert_pdf_to_word(word_path, word_path)

        # Notify user of the conversion status
        await message.reply(f"Conversion of {pdf_path} to {word_path} started. You will be notified when it's done.")
    else:
        await message.reply("Please send a PDF document to convert!")

# Register this handler
def register_handlers(dp):
    dp.register_message_handler(handle_pdf, content_types=types.ContentType.DOCUMENT)
