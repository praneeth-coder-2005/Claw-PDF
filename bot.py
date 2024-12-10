import logging
import os
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

# --- Replace with your actual bot token ---
API_TOKEN = '7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M'

# --- Set up logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Install necessary libraries ---
# pip install PyPDF2 Pillow reportlab
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --- Global variables ---
user_states = {}  # To track user's current operation
UPLOAD_PDF, UPLOAD_PDF_2 = range(2)  # Conversation states for file uploads

# --- Keyboard functions ---
# ... (Include all the keyboard functions from the previous response) ...

# --- Command and Callback Handlers ---
# ... (Include the start and button handlers from the previous response) ...

# --- Conversation handler for multi-file uploads (e.g., merge_pdf) ---
# ... (Include the upload_pdf and upload_pdf_2 handlers from the previous response) ...

# --- Message handler for single file uploads ---

async def handle_pdf_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles uploaded PDF files for single-file operations."""
    user_id = update.message.from_user.id
    if user_id in user_states:
        action = user_states[user_id]
        file = await update.message.document.get_file()
        pdf_data = BytesIO(await file.download_as_bytearray())

        try:
            if action == 'pdf_to_word':
                await update.message.reply_text("This feature is not yet implemented. We are working on it!")
                # --- PDF to Word conversion is complex and requires advanced libraries
                # You might need to use OCR and other techniques for accurate conversion
                # Consider using libraries like 'pdfminer' or 'pytesseract' for OCR

            elif action == 'pdf_to_excel':
                await update.message.reply_text("This feature is not yet implemented. We are working on it!")
                # --- Similar to PDF to Word, this requires advanced techniques
                # You might need to analyze the PDF structure and extract tabular data
                # Libraries like 'camelot' or 'tabula-py' can be helpful

            elif action == 'pdf_to_powerpoint':
                await update.message.reply_text("This feature is not yet implemented. We are working on it!")
                # --- This involves extracting text and images from PDF and creating slides
                # Libraries like 'python-pptx' can be used for PowerPoint generation

            elif action == 'merge_pdf':
                await update.message.reply_text("Your PDF files are being merged. Please wait...")
                merger = PdfMerger()
                merger.append(pdf_data)
                merger.append(context.user_data['pdf1'])  # Assuming you stored the first PDF in user_data
                output_buffer = BytesIO()
                merger.write(output_buffer)
                output_buffer.seek(0)
                await update.message.reply_document(output_buffer, filename="merged.pdf")

            elif action == 'split_pdf':
                await update.message.reply_text("This feature is not yet implemented. We are working on it!")
                # --- You'll need to get the split point (page number) from the user
                # Then use PyPDF2 to split the PDF into two or more parts

            elif action == 'compress_pdf':
                await update.message.reply_text("This feature is not yet implemented. We are working on it!")
                # --- PDF compression can be achieved by reducing image quality, 
                # downsampling images, and optimizing fonts.
                # Libraries like 'PyPDF2' and 'Ghostscript' can be used

            elif action == 'rotate_pdf':
                await update.message.reply_text("Please enter the rotation angle (90, 180, or 270 degrees):", reply_markup=ForceReply())
                user_states[user_id] = 'rotate_pdf_angle'  # Move to the next state to get the angle

            elif action == 'add_page_numbers':
                await update.message.reply_text("This feature is not yet implemented. We are working on it!")
                # --- You can use PyPDF2 and reportlab to add page numbers to each page

            elif action == 'add_watermark':
                await update.message.reply_text("This feature is not yet implemented. We are working on it!")
                # --- Use PyPDF2 and reportlab to add a watermark (text or image) to each page

            # ... (Add other actions here - repair_pdf, unlock_pdf, etc.) ...

        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            await update.message.reply_text("An error occurred while processing your PDF.")

        del user_states[user_id]  # Clear the user's state


async def handle_rotation_angle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the rotation angle input for rotate_pdf."""
    user_id = update.message.from_user.id
    angle = int(update.message.text)  # Get the angle from the user's message
    if angle in (90, 180, 270):
        try:
            # ... (Get the original PDF data from user_data or previous step) ...
            pdf_reader = PdfReader(pdf_data)
            pdf_writer = PdfWriter()
            for page in pdf_reader.pages:
                page.rotate(angle)
                pdf_writer.add_page(page)
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            await update.message.reply_document(output_buffer, filename="rotated.pdf")
        except Exception as e:
            logging.error(f"Error rotating PDF: {e}")
            await update.message.reply_text("An error occurred while rotating your PDF.")
    else:
        await update.message.reply_text("Invalid rotation angle. Please enter 90, 180, or 270.")
    del user_states[user_id]


def main():
    """Start the bot."""
    # ... (Register handlers - same as in the previous response) ...

    # --- Add the new handler for rotation angle input ---
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rotation_angle))

    # Run the bot until you press Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
