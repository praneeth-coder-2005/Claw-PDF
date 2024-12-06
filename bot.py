import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters
from telegram.error import TelegramError
from PyPDF2 import PdfMerger
from flask import Flask, request

# Initialize Flask App
app = Flask(__name__)

# Bot Token and Render URL
BOT_TOKEN = "7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M"
WEBHOOK_URL = f"https://claw-pdf.onrender.com/{BOT_TOKEN}"

# Temporary directory for processing files
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Application instance
application = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Bot Commands and Handlers ---

# Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to the ILovePDF Bot! 🌟\n"
        "I can help you with various PDF tasks like merging, splitting, compressing, and more.\n\n"
        "Use the commands to get started:\n"
        "/help - List of commands"
    )

# Help Command
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Here are the commands you can use:\n"
        "/merge - Merge multiple PDFs\n"
        "/split - Split a PDF into multiple files\n"
        "/compress - Compress a PDF\n"
        "/convert - Convert images to PDF\n"
        "/extract_text - Extract text from a PDF (OCR)\n"
        "/help - Show this help message\n"
    )

# Merge PDFs
async def merge_pdfs(update: Update, context: CallbackContext):
    files = context.user_data.get("merge_files", [])
    if not files:
        context.user_data["merge_files"] = []
        await update.message.reply_text("Send me PDFs one by one. Type /done when finished.")
    else:
        merger = PdfMerger()
        for file in files:
            merger.append(file)
        output_path = os.path.join(TEMP_DIR, "merged.pdf")
        merger.write(output_path)
        merger.close()

        with open(output_path, "rb") as f:
            await update.message.reply_document(document=f, filename="merged.pdf")

        # Clear user data
        context.user_data["merge_files"] = []

# Collect Files
async def collect_files(update: Update, context: CallbackContext):
    if not context.user_data.get("merge_files"):
        context.user_data["merge_files"] = []

    file = update.message.document
    if file and file.mime_type == "application/pdf":
        file_path = os.path.join(TEMP_DIR, file.file_name)

        # Properly await get_file and download it
        try:
            file_data = await file.get_file()
            await file_data.download(custom_path=file_path)

            context.user_data["merge_files"].append(file_path)
            await update.message.reply_text(f"Added {file.file_name}. Send more files or type /done to merge.")
        except TelegramError as e:
            await update.message.reply_text(f"Failed to download file: {str(e)}")
    else:
        await update.message.reply_text("Please send a valid PDF file.")

# Complete Merge
async def done(update: Update, context: CallbackContext):
    await merge_pdfs(update, context)

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
    application.add_handler(CommandHandler("merge", merge_pdfs))
    application.add_handler(CommandHandler("done", done))
    application.add_handler(MessageHandler(filters.Document.ALL, collect_files))

    # Set Webhook for Render
    port = int(os.environ.get("PORT", 8443))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL
    )
    app.run(host="0.0.0.0", port=port)
