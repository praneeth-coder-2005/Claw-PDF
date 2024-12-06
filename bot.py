import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from telegram.error import TelegramError
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from PIL import Image

# Flask App
app = Flask(__name__)

# Bot Configuration
BOT_TOKEN = "7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M"
WEBHOOK_URL = f"https://claw-pdf.onrender.com/{BOT_TOKEN}"
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Application Instance
application = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Bot Commands and Features ---

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
        [
            InlineKeyboardButton("Extract Images", callback_data="extract_images"),
            InlineKeyboardButton("Password Protect", callback_data="password_protect"),
        ],
        [InlineKeyboardButton("Rotate Pages", callback_data="rotate_pages")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Advanced ILovePDF Bot! 🌟\nI can assist with a wide range of PDF tasks. Choose an option below:",
        reply_markup=reply_markup,
    )

# Help Command
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Here are the advanced features I offer:\n\n"
        "- **Merge PDFs**: Combine multiple PDFs into one.\n"
        "- **Split PDF**: Split a PDF into multiple parts.\n"
        "- **Compress PDF**: Reduce the file size of a PDF.\n"
        "- **Extract Text**: Extract text content from a PDF.\n"
        "- **Extract Images**: Extract all images from a PDF.\n"
        "- **Password Protect**: Add or remove password protection from a PDF.\n"
        "- **Rotate Pages**: Rotate pages by specified angles.\n\n"
        "Send files and commands as instructed, and I will process them promptly!"
    )

# Callback Handler for Inline Buttons
async def handle_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    context.user_data["task"] = data

    task_messages = {
        "merge": "Send me the PDFs to merge. Type /done when finished.",
        "split": "Send me the PDF to split.",
        "compress": "Send me the PDF to compress.",
        "extract_text": "Send me the PDF to extract text from.",
        "extract_images": "Send me the PDF to extract images from.",
        "password_protect": "Send me the PDF to add/remove password protection.",
        "rotate_pages": "Send me the PDF to rotate pages.",
    }

    await query.edit_message_text(task_messages.get(data, "Invalid task selected."))

# Collect Files
async def collect_files(update: Update, context: CallbackContext):
    task = context.user_data.get("task")
    if not task:
        await update.message.reply_text("Please select a task first using the /start command.")
        return

    file = update.message.document
    if not file:
        await update.message.reply_text("Please send a valid file.")
        return

    file_path = os.path.join(TEMP_DIR, file.file_name)
    try:
        file_data = await file.get_file()
        await file_data.download_to_drive(file_path)
        context.user_data.setdefault("files", []).append(file_path)
        await update.message.reply_text(f"File {file.file_name} received.")
    except TelegramError as e:
        await update.message.reply_text(f"Error downloading file: {e}")

# Done Command for Processing
async def done(update: Update, context: CallbackContext):
    task = context.user_data.get("task")
    files = context.user_data.get("files", [])

    if task == "merge":
        if len(files) < 2:
            await update.message.reply_text("Please send at least two PDFs to merge.")
            return

        merger = PdfMerger()
        for file in files:
            merger.append(file)
        output_path = os.path.join(TEMP_DIR, "merged.pdf")
        merger.write(output_path)
        merger.close()

        with open(output_path, "rb") as f:
            await update.message.reply_document(document=f, filename="merged.pdf")

        cleanup_temp(files + [output_path])
        context.user_data.clear()

    else:
        await update.message.reply_text("Task not supported for /done command.")

# Rotate Pages
async def rotate_pages(update: Update, context: CallbackContext):
    files = context.user_data.get("files", [])
    if not files:
        await update.message.reply_text("No files uploaded. Please send a PDF first.")
        return

    file_path = files[0]
    angle = 90  # Example rotation angle
    reader = PdfReader(file_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    output_path = os.path.join(TEMP_DIR, "rotated.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    with open(output_path, "rb") as f:
        await update.message.reply_document(document=f, filename="rotated.pdf")

    cleanup_temp([file_path, output_path])
    context.user_data.clear()

# Cleanup Temporary Files
def cleanup_temp(file_list):
    for file in file_list:
        if os.path.exists(file):
            os.remove(file)

# Flask Webhook Route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return "OK", 200

# Main Function
if __name__ == "__main__":
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("done", done))
    application.add_handler(MessageHandler(filters.Document.ALL, collect_files))
    application.add_handler(CallbackQueryHandler(handle_buttons))

    port = int(os.environ.get("PORT", 8443))
    application.run_webhook(
        listen="0.0.0.0", port=port, url_path=BOT_TOKEN, webhook_url=WEBHOOK_URL
    )
    app.run(host="0.0.0.0", port=port)
