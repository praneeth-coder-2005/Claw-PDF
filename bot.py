import logging
import os
from io import BytesIO
from telegram import Update, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
import img2pdf

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "7913483326:AAGWXALKIt9DJ_gemT8EpC5h_yKWUCzH37M"


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Hi {user.mention_markdown_v2()}!",
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def convert_image(update: Update, context: CallbackContext) -> None:
    """Convert an image to PDF and send it back to the user."""
    if not update.message.photo:
        update.message.reply_text("Please send me an image to convert.")
        return

    # Get the largest photo
    photo = update.message.photo[-1]
    file_id = photo.file_id
    new_file = context.bot.get_file(file_id)

    # Download the image
    image_data = BytesIO(new_file.download_as_bytearray())

    # Convert the image to PDF
    pdf_bytes = img2pdf.convert(image_data.getvalue())

    # Send the PDF back to the user
    update.message.reply_document(
        document=pdf_bytes,
        filename="converted.pdf",
        caption="Here is your converted PDF file.",
    )


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN, use_context=True)  # Add use_context=True

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - convert the image to pdf
    dispatcher.add_handler(MessageHandler(filters.PHOTO, convert_image))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
    
