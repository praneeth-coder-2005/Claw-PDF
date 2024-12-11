import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image
import io

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('YOUR_BOT_TOKEN')

def create_pdf(image_file):
    """Converts an image file to a PDF file."""
    image = Image.open(image_file)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PDF')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    """Handles photo messages and converts them to PDF."""
    try:
        # Get the file ID of the largest photo size
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)

        # Download the image file
        downloaded_file = bot.download_file(file_info.file_path)

        # Convert the image to PDF
        pdf_file = create_pdf(io.BytesIO(downloaded_file))

        # Create inline keyboard with download button
        keyboard = InlineKeyboardMarkup()
        download_button = InlineKeyboardButton("Download PDF", callback_data="download_pdf")
        keyboard.add(download_button)

        # Send the PDF file with the inline keyboard
        bot.send_document(message.chat.id, pdf_file, caption="Here's your PDF file!", reply_markup=keyboard)

    except Exception as e:
        bot.reply_to(message, f"Sorry, something went wrong: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Handles callback queries from inline buttons."""
    if call.data == "download_pdf":
        # Resend the PDF file (you might want to store the file ID for efficiency)
        # For this example, we'll just repeat the conversion process
        file_id = call.message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        pdf_file = create_pdf(io.BytesIO(downloaded_file))
        bot.send_document(call.message.chat.id, pdf_file, caption="Here's your PDF file again!")

# Start the bot
bot.polling()
    
