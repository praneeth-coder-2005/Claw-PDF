import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image
import io
import logging
from PyPDF2 import PdfMerger

# Configure logging
logging.basicConfig(filename='telegram_bot.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('YOUR_BOT_TOKEN')

# Global list to store PDF files for merging
pdf_files_to_merge = []

def create_pdf(image_file):
    """Converts an image file to a PDF file."""
    try:
        image = Image.open(image_file)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PDF', resolution=100.0) 
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr
    except Exception as e:
        logging.error(f"Error converting image to PDF: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Sends a welcome message with inline buttons."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    convert_button = InlineKeyboardButton("Convert Image to PDF", callback_data="convert_image")
    merge_button = InlineKeyboardButton("Merge PDFs", callback_data="merge_pdfs")
    keyboard.add(convert_button, merge_button)

    bot.reply_to(message, "Hello! I can convert images to PDF files and merge PDFs. \n\n"
                          "To convert, send me an image. To merge, click the 'Merge PDFs' button.", reply_markup=keyboard)

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

        if pdf_file:
            # Create inline keyboard with download button
            keyboard = InlineKeyboardMarkup()
            download_button = InlineKeyboardButton("Download PDF", callback_data="download_pdf")
            keyboard.add(download_button)

            # Send the PDF file with the inline keyboard
            bot.send_document(message.chat.id, pdf_file, filename="converted_image.pdf", caption="Here's your PDF file!", reply_markup=keyboard)
        else:
            bot.reply_to(message, "Sorry, I couldn't convert your image to PDF. Please try again later.")

    except Exception as e:
        logging.error(f"Error handling image: {e}")
        bot.reply_to(message, "Sorry, something went wrong. Please try again later.")

@bot.message_handler(content_types=['document'])
def handle_pdf(message):
    """Handles PDF documents for merging."""
    try:
        if message.document.mime_type == 'application/pdf':
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            pdf_files_to_merge.append(io.BytesIO(downloaded_file))

            # Ask if the user wants to merge immediately after adding a PDF
            keyboard = InlineKeyboardMarkup()
            merge_now_button = InlineKeyboardButton("Merge Now", callback_data="merge_now")
            keyboard.add(merge_now_button)
            bot.reply_to(message, "PDF file received and added to the merge list! Do you want to merge now?", reply_markup=keyboard)

        else:
            bot.reply_to(message, "Please send a PDF file.")
    except Exception as e:
        logging.error(f"Error handling PDF document: {e}")
        bot.reply_to(message, "Sorry, something went wrong. Please try again later.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Handles callback queries from inline buttons."""
    try:
        if call.data == "download_pdf":
            # Resend the PDF file 
            file_id = call.message.document.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            pdf_file = create_pdf(io.BytesIO(downloaded_file))
            if pdf_file:
                bot.send_document(call.message.chat.id, pdf_file, caption="Here's your PDF file again!")
            else:
                bot.answer_callback_query(call.id, "Sorry, I couldn't retrieve the PDF file.")
        elif call.data == "convert_image":
            bot.send_message(call.message.chat.id, "Please send me the image you want to convert to PDF.") 
        elif call.data == "merge_pdfs":
            # Send a message with an inline button to start sending PDFs
            keyboard = InlineKeyboardMarkup()
            send_pdf_button = InlineKeyboardButton("Send PDFs", callback_data="send_pdfs")
            keyboard.add(send_pdf_button)
            bot.send_message(call.message.chat.id, "Please send the PDF files you want to merge.", reply_markup=keyboard)
        elif call.data == "send_pdfs":
            bot.send_message(call.message.chat.id, "Start sending your PDF files now!")
        elif call.data == "merge_now":
            if len(pdf_files_to_merge) < 2:
                bot.answer_callback_query(call.id, "Please send at least 2 PDF files to merge.")
            else:
                try:
                    merger = PdfMerger()
                    for pdf_file in pdf_files_to_merge:
                        merger.append(pdf_file)

                    merged_pdf = io.BytesIO()
                    merger.write(merged_pdf)
                    merger.close()
                    merged_pdf.seek(0)

                    bot.send_document(call.message.chat.id, merged_pdf, caption="Here's your merged PDF!")
                    pdf_files_to_merge.clear()  # Clear the list after merging

                except Exception as e:
                    logging.error(f"Error merging PDFs: {e}")
                    bot.answer_callback_query(call.id, "Sorry, something went wrong while merging the PDFs.")
    except Exception as e:
        logging.error(f"Error handling callback query: {e}")
        bot.answer_callback_query(call.id, "Sorry, something went wrong.")

# Start the bot
try:
    bot.polling()
except Exception as e:
    logging.error(f"Bot polling failed: {e}")
  
