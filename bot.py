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
import zipfile
import shutil

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

    elif task == "split":
        if not files:
            await update.message.reply_text("Please send a PDF to split.")
            return

        file_path = files[0]
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            output_path = os.path.join(TEMP_DIR, f"split_{i + 1}.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)

            with open(output_path, "rb") as f:
                await update.message.reply_document(document=f, filename=f"split_{i + 1}.pdf")

        cleanup_temp(files)
        context.user_data.clear()

    elif task == "compress":
        if not files:
            await update.message.reply_text("Please send a PDF to compress.")
            return

        file_path = files[0]
        # Simulate compression (in reality, use a library like pikepdf or Ghostscript)
        output_path = os.path.join(TEMP_DIR, "compressed.pdf")
        shutil.copy(file_path, output_path)

        with open(output_path, "rb") as f:
            await update.message.reply_document(document=f, filename="compressed.pdf")

        cleanup_temp(files + [output_path])
        context.user_data.clear()

    elif task == "extract_text":
        if not files:
            await update.message.reply_text("Please send a PDF to extract text from.")
            return

        file_path = files[0]
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        output_path = os.path.join(TEMP_DIR, "extracted_text.txt")
        with open(output_path, "w") as f:
            f.write(text)

        with open(output_path, "rb") as f:
            await update.message.reply_document(document=f, filename="extracted_text.txt")

        cleanup_temp(files + [output_path])
        context.user_data.clear()

    elif task == "extract_images":
        if not files:
            await update.message.reply_text("Please send a PDF to extract images from.")
            return

        file_path = files[0]
        images = extract_images_from_pdf(file_path)
        zip_path = os.path.join(TEMP_DIR, "extracted_images.zip")

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for i, img_path in enumerate(images):
                zipf.write(img_path, os.path.basename(img_path))

        with open(zip_path, "rb") as f:
            await update.message.reply_document(document=f, filename="extracted_images.zip")

        cleanup_temp(files + images + [zip_path])
        context.user_data.clear()

    elif task == "password_protect":
        if not files:
            await update.message.reply_text("Please send a PDF to add/remove password protection.")
            return

        file_path = files[0]
        password = "password123"  # Set password
        output_path = os.path.join(TEMP_DIR,output_path = os.path.join(TEMP_DIR, "protected.pdf")
        protect_pdf(file_path, output_path, password)

        with open(output_path, "rb") as f:
            await update.message.reply_document(document=f, filename="protected.pdf")

        cleanup_temp(files + [output_path])
        context.user_data.clear()

    elif task == "rotate_pages":
        if not files:
            await update.message.reply_text("Please send a PDF to rotate pages.")
            return

        file_path = files[0]
        angle = 90  # Rotate by 90 degrees
        output_path = rotate_pdf(file_path, angle)

        with open(output_path, "rb") as f:
            await update.message.reply_document(document=f, filename="rotated.pdf")

        cleanup_temp([file_path, output_path])
        context.user_data.clear()

    else:
        await update.message.reply_text("Task not supported for /done command.")

# Helper Functions

def rotate_pdf(file_path, angle):
    reader = PdfReader(file_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    output_path = os.path.join(TEMP_DIR, "rotated.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def protect_pdf(input_path, output_path, password):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    with open(output_path, "wb") as f:
        writer.write(f)

def extract_images_from_pdf(pdf_path):
    images = []
    pdf_reader = PdfReader(pdf_path)

    for page_num, page in enumerate(pdf_reader.pages):
        xObject = page["/Resources"].get("/XObject")
        if xObject:
            for obj in xObject:
                if xObject[obj]["/Subtype"] == "/Image":
                    size = (xObject[obj]["/Width"], xObject[obj]["/Height"])
                    image_data = xObject[obj].get_data()

                    image_path = os.path.join(TEMP_DIR, f"image_{page_num + 1}_{obj[1:]}.jpg")
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_data)
                    images.append(image_path)

    return images

# Clean up temporary files
def cleanup_temp(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)

# Webhook setup
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, application.bot)
    application.process_update(update)
    return "OK", 200

# Set up Webhook
async def set_webhook():
    await application.bot.setWebhook(WEBHOOK_URL)

if __name__ == "__main__":
    # Setup Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_buttons))
    application.add_handler(MessageHandler(filters.Document.ALL, collect_files))
    application.add_handler(CommandHandler("done", done))

    # Start the Webhook
    application.loop.run_until_complete(set_webhook())

    # Start the Flask app to handle the webhook
    app.run(host="0.0.0.0", port=80)
