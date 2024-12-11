import logging
import os
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Replace with your actual token

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

def build_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Convert PDF", callback_data='convert'),
            InlineKeyboardButton("Organize PDF", callback_data='organize')
        ],
        [
            InlineKeyboardButton("Optimize PDF", callback_data='optimize'),
            InlineKeyboardButton("Edit PDF", callback_data='edit')
        ],
        [
            InlineKeyboardButton("PDF Security", callback_data='security'),
            InlineKeyboardButton("Other Tools", callback_data='other')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_convert_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("PDF to Word", callback_data='pdf_to_word')],
        [InlineKeyboardButton("PDF to Excel", callback_data='pdf_to_excel')],
        [InlineKeyboardButton("PDF to PowerPoint", callback_data='pdf_to_powerpoint')],
        [InlineKeyboardButton("Word to PDF", callback_data='word_to_pdf')],
        [InlineKeyboardButton("Excel to PDF", callback_data='excel_to_pdf')],
        [InlineKeyboardButton("PowerPoint to PDF", callback_data='powerpoint_to_pdf')],
        [InlineKeyboardButton("JPG to PDF", callback_data='jpg_to_pdf')],
        [InlineKeyboardButton("PDF to JPG", callback_data='pdf_to_jpg')],
        [InlineKeyboardButton("PDF to PDF/A", callback_data='pdf_to_pdfa')],
        [InlineKeyboardButton("HTML to PDF", callback_data='html_to_pdf')],
        [InlineKeyboardButton("Back to Main Menu", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_organize_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Merge PDF", callback_data='merge_pdf')],
        [InlineKeyboardButton("Split PDF", callback_data='split_pdf')],
        [InlineKeyboardButton("Compress PDF", callback_data='compress_pdf')],
        [InlineKeyboardButton("Rotate PDF", callback_data='rotate_pdf')],
        [InlineKeyboardButton("Add page numbers", callback_data='add_page_numbers')],
        [InlineKeyboardButton("Add watermark", callback_data='add_watermark')],
        [InlineKeyboardButton("Remove PDF pages", callback_data='remove_pdf_pages')],
        [InlineKeyboardButton("Reorder PDF pages", callback_data='reorder_pdf_pages')],
        [InlineKeyboardButton("Organize PDF pages", callback_data='organize_pdf_pages')],
        [InlineKeyboardButton("Back to Main Menu", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ... (Add other keyboard functions for optimize, edit, security, other) ...


# --- Command and Callback Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Welcome to the Claw PDF Bot!', reply_markup=build_main_menu_keyboard())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # --- Menu navigation ---
    if query.data == 'convert':
        await query.edit_message_text(text="Choose a conversion option:", reply_markup=build_convert_menu_keyboard())
    elif query.data == 'organize':
        await query.edit_message_text(text="Choose an organization option:", reply_markup=build_organize_menu_keyboard())
    # ... (Handle other menu options - optimize, edit, security, other) ...
    elif query.data == 'main_menu':
        await query.edit_message_text(text="Claw PDF Bot Main Menu:", reply_markup=build_main_menu_keyboard())

    # --- Feature actions ---
    elif query.data == 'pdf_to_word':
        user_states[user_id] = 'pdf_to_word'
        await query.edit_message_text(
            text="Please upload the PDF file you want to convert to Word.",
            reply_markup=ForceReply(force_reply=True, input_field_placeholder="Upload PDF")
        )
    elif query.data == 'merge_pdf':
        user_states[user_id] = 'merge_pdf'
        await query.edit_message_text(text="Please upload the first PDF file you want to merge.", reply_markup=ForceReply())
        return UPLOAD_PDF  # Enter the conversation state to handle multiple file uploads
    elif query.data == 'split_pdf':
        user_states[user_id] = 'split_pdf'
        await query.edit_message_text(text="Please upload the PDF file you want to split.", reply_markup=ForceReply())
    elif query.data == 'rotate_pdf':
        user_states[user_id] = 'rotate_pdf'
        await query.edit_message_text(text="Please upload the PDF file you want to rotate.", reply_markup=ForceReply())
    # ... (Add other feature actions - pdf_to_excel, etc.) ...


# --- Conversation handler for multi-file uploads (e.g., merge_pdf) ---

async def upload_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the first PDF upload in a multi-file upload process."""
    user_id = update.message.from_user.id
    file = await update.message.document.get_file()
    context.user_data['pdf1'] = BytesIO(await file.download_as_bytearray())
    await update.message.reply_text("Please upload the second PDF file.")
    return UPLOAD_PDF_2  # Move to the next state to get the second file

async def upload_pdf_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the second PDF upload in a multi-file upload process."""
    user_id = update.message.from_user.id
    file = await update.message.document.get_file()
    context.user_data['pdf2'] = BytesIO(await file.download_as_bytearray())

    await update.message.reply_text("Merging your PDF files...")
    try:
        merger = PdfMerger()
        merger.append(context.user_data['pdf1'])
        merger.append(context.user_data['pdf2'])
        output_buffer = BytesIO()
        merger.write(output_buffer)
        output_buffer.seek(0)
        await update.message.reply_document(output_buffer, filename="merged.pdf")
    except Exception as e:
        logging.error(f"Error merging PDFs: {e}")
        await update.message.reply_text("An error occurred while merging your PDFs.")

    del user_states[user_id]  # Clear the user's state
    return ConversationHandler.END  # End the conversation


# --- Message handler for single file uploads ---

async def handle_pdf_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles uploaded PDF files for single-file operations."""
    user_id = update.message.from_user.id
    if user_id in user_states:
        action = user_states[user_id]
        file = await update.message.document.get_file()
        pdf_data = BytesIO(await file.download_as_bytearray())
        context.user_data['pdf_data'] = pdf_data  # Store PDF data in user_data

        try:
            if action == 'pdf_to_word':
                await update.message.reply_text("This feature is not yet implemented. We are working on it!")

            elif action == 'split_pdf':
                await update.message.reply_text("Splitting your PDF file...")
                try:
                    pdf_reader = PdfReader(pdf_data)
                    for i in range(len(pdf_reader.pages)):
                        pdf_writer = PdfWriter()
                        pdf_writer.add_page(pdf_reader.pages[i])
                        output_buffer = BytesIO()
                        pdf_writer.write(output_buffer)
                        output_buffer.seek(0)
                        await update.message.reply_document(output_buffer, filename=f"split_{i+1}.pdf")
                except Exception as e:
                    logging.error(f"Error splitting PDF: {e}")
                    await update.message.reply_text("An error occurred while splitting your PDF.")

            elif action == 'rotate_pdf':
                await update.message.reply_text(
                    "Please enter the rotation angle (90, 180, or 270 degrees):",
                    reply_markup=ReplyKeyboardMarkup([['90'], ['180'], ['270']], one_time_keyboard=True)
                )
                user_states[user_id] = 'rotate_pdf_angle'  # Move to the next state to get the angle

            # ... (Add other feature actions - pdf_to_excel, etc.) ...

        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            await update.message.reply_text("An error occurred while processing your PDF.")

        if action not in ('rotate_pdf', 'rotate_pdf_angle'):  # Don't delete state for rotate operation yet
            del user_states[user_id]  # Clear the user's state


async def handle_rotation_angle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the rotation angle input for rotate_pdf."""
    user_id = update.message.from_user.id
    try:
        angle = int(update.message.text)  # Get the angle from the user's message
        if angle in (90, 180, 270):
            pdf_data = context.user_data.get('pdf_data')
            if pdf_data:
                pdf_reader = PdfReader(pdf_data)
                pdf_writer = PdfWriter()
                for page in pdf_reader.pages:
                    page.rotate(angle)
                    pdf_writer.add_page(page)
                output_buffer = BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
                await update.message.reply_document(
                    document=output_buffer,
                    filename="rotated.pdf",
                    reply_markup=ReplyKeyboardRemove()  # Remove the reply keyboard
                )
            else:
                await update.message.reply_text("Please upload the PDF file first.")
        else:
            await update.message.reply_text("Invalid rotation angle. Please enter 90, 180, or 270.")
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a valid number for the rotation angle.")
    except Exception as e:
        logging.error(f"Error rotating PDF: {e}")
        await update.message.reply_text("An error occurred while rotating your PDF.")
    finally:
        del user_states[user_id]


def main():
    """Start the bot."""
    application = ApplicationBuilder().token(API_TOKEN).build()

    # --- Register handlers ---
    application.add_handler(CommandHandler('start', start))

    # --- CallbackQueryHandlers for all patterns ---
    application.add_handler(CallbackQueryHandler(button, pattern='convert'))
    application.add_handler(CallbackQueryHandler(button, pattern='organize'))
    # ... (Add CallbackQueryHandlers for other menu options) ...
    application.add_handler(CallbackQueryHandler(button, pattern='main_menu'))
    # ... (Add CallbackQueryHandlers for feature actions) ...

    # --- Conversation handler for multi-file uploads ---
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button, pattern='merge_pdf')],
        states={
            UPLOAD_PDF: [MessageHandler(filters.Document.MimeType("application/pdf"), upload_pdf)],
            UPLOAD_PDF_2: [MessageHandler(filters.Document.MimeType("application/pdf"), upload_pdf_2)],
        },
        fallbacks=[],  # You can add fallback handlers if needed
    )
    application.add_handler(conv_handler)

    # --- Message handler for single file uploads ---
    application.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), handle_pdf_upload))

    # --- Add the handler for rotation angle input ---
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rotation_angle))

    # Run the bot until you press Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
