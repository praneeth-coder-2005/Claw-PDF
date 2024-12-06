import os
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2image import convert_from_path
import img2pdf
import tempfile

# Bot Token from BotFather
BOT_TOKEN = "7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M"

# Temporary directory for processing files
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)


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

        context.user_data["merge_files"] = []


# Collecting Files
async def collect_files(update: Update, context: CallbackContext):
    if not context.user_data.get("merge_files"):
        context.user_data["merge_files"] = []

    file = update.message.document
    if file and file.mime_type == "application/pdf":
        file_path = os.path.join(TEMP_DIR, file.file_name)
        await file.get_file().download_to_drive(file_path)
        context.user_data["merge_files"].append(file_path)
        await update.message.reply_text(f"Added {file.file_name}. Send more files or type /done to merge.")
    else:
        await update.message.reply_text("Please send a valid PDF file.")


# Complete Merge
async def done(update: Update, context: CallbackContext):
    await merge_pdfs(update, context)


# Split PDFs
async def split_pdf(update: Update, context: CallbackContext):
    await update.message.reply_text("Send me the PDF file you want to split.")


# Handling File Uploads
async def handle_file_upload(update: Update, context: CallbackContext):
    file = update.message.document
    if file.mime_type == "application/pdf":
        file_path = os.path.join(TEMP_DIR, file.file_name)
        await file.get_file().download_to_drive(file_path)
        await update.message.reply_text(f"Received {file.file_name}. Now processing...")
        # Implement PDF handling logic
    else:
        await update.message.reply_text("Please upload a valid PDF file.")


# Main Function
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("merge", merge_pdfs))
    application.add_handler(CommandHandler("done", done))
    application.add_handler(MessageHandler(filters.Document.ALL, collect_files))

    application.run_polling()


if __name__ == "__main__":
    main()
