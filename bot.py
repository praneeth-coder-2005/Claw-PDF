import os
import shutil
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from telegram.error import TelegramError
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
from flask import Flask, request
import logging

# Flask App
app = Flask(__name__)

# Bot Token and Render URL
BOT_TOKEN = "7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M"
WEBHOOK_URL = f"https://claw-pdf.onrender.com/{BOT_TOKEN}"

# Temporary directory for processing files
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Application instance
application = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Bot Commands and Handlers ---

# Start Command
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Help", callback_data="help")],
        [
            InlineKeyboardButton("Merge PDFs", callback_data="merge"),
            InlineKeyboardButton("Split PDF", callback_data="split"),
        ],
        [
            InlineKeyboardButton("Compress PDF", callback_data="compress"),
            InlineKeyboardButton("Extract Text", callback_data="extract_text"),
        ],
        [InlineKeyboardButton("Extract Images", callback_data="extract_images")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the ILovePDF Bot! 🌟\nI can help you with various PDF tasks. Choose an option below:",
        reply_markup=reply_markup,
    )

# Help Command
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Here are the features I offer:\n\n"
        "- **Merge PDFs:** Combine multiple PDFs into one.\n"
        "- **Split PDF:** Split a PDF into multiple files.\n"
        "- **Compress PDF:** Reduce the file size of a PDF.\n"
        "- **Extract Text:** Extract text from a PDF.\n"
        "- **Extract Images:** Extract all images from a PDF.\n"
        "- **Convert Images to PDF:** Send images to convert them to a PDF.\n\n"
        "Use the buttons below the commands for a better experience!"
    )

# Callback for Inline Buttons
async def handle_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "help":
        await help_command(update, context)
    elif data == "merge":
        context.user_data["task"] = "merge"
        context.user_data["files"] = []
        await query.edit_message_text("Send me the PDFs to merge. Type /done when finished.")
    elif data == "split":
        context.user_data["task"] = "split"
        await query.edit_message_text("Send me the PDF to split.")
    elif data == "compress":
        context.user_data["task"] = "compress"
        await query.edit_message_text("Send me the PDF to compress.")
    elif data == "extract_text":
        context.user_data["task"] = "extract_text"
        await query.edit_message_text("Send me the PDF to extract text from.")
    elif data == "extract_images":
        context.user_data["task"] = "extract_images"
        await query.edit_message_text("Send me the PDF to extract images from.")

# Collect Files
async def collect_files(update: Update, context: CallbackContext):
    task = context.user_data.get("task")
    if not task:
        await update.message.reply_text("Please select a task first using the /start command.")
        return

    file = update.message.document
    if not file or file.mime_type != "application/pdf":
        await update.message.reply_text("Please send a valid PDF file.")
        return

    file_path = os.path.join(TEMP_DIR, file.file_name)

    try:
        file_data = await file.get_file()
        await file_data.download_to_drive(file_path)
        context.user_data.setdefault("files", []).append(file_path)

        if task == "merge":
            await update.message.reply_text(
                f"Added {file.file_name}. Send more files or type /done to merge."
            )
        elif task in ["split", "compress", "extract_text", "extract_images"]:
            context.user_data["single_file"] = file_path
            await update.message.reply_text(f"File {file.file_name} received. Processing...")
    except TelegramError as e:
        await update.message.reply_text(f"Failed to download file: {str(e)}")

# Merge PDFs
async def merge_pdfs(update: Update, context: CallbackContext):
    files = context.user_data.get("files", [])
    if not files:
        await update.message.reply_text("No files to merge. Please send PDFs first.")
        return

    merger = PdfMerger()
    for file in files:
        merger.append(file)
    output_path = os.path.join(TEMP_DIR, "merged.pdf")
    merger.write(output_path)
    merger.close()

    with open(output_path, "rb") as f:
        await update.message.reply_document(document=f, filename="merged.pdf")

    # Clean up
    for file in files:
        os.remove(file)
    context.user_data.clear()

# Done Command
async def done(update: Update, context: CallbackContext):
    task = context.user_data.get("task")
    if task == "merge":
        await merge_pdfs(update, context)
    else:
        await update.message.reply_text("This command is only for merging. Use appropriate commands.")

# --- Flask Webhook Route ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return "OK", 200

# --- Main Function ---
if __name__ == "__main__":
    # Add Handlers to Application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("done", done))
    application.add_handler(MessageHandler(filters.Document.ALL, collect_files))
    application.add_handler(CallbackQueryHandler(handle_buttons))

    # Set Webhook for Render
    port = int(os.environ.get("PORT", 8443))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL,
    )
    app.run(host="0.0.0.0", port=port)
