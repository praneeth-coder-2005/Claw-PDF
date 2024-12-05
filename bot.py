import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from config import API_TOKEN, UPLOAD_FOLDER
from handlers.merge import merge_pdfs
from handlers.compress import compress_pdf

# Initialize the bot
bot = telebot.TeleBot(API_TOKEN)

# Ensure uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory user session data (for tracking file uploads per user)
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Merge PDF", callback_data="merge"),
        InlineKeyboardButton("Split PDF", callback_data="split"),
        InlineKeyboardButton("Compress PDF", callback_data="compress")
    )
    bot.send_message(chat_id, "Welcome to the PDF Bot! Select a feature:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "merge")
def merge_handler(call):
    chat_id = call.message.chat.id
    user_data[chat_id] = {'action': 'merge', 'files': []}
    bot.send_message(chat_id, "Please send the PDFs you want to merge. Type /done when finished.")

@bot.message_handler(content_types=['document'])
def handle_files(message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id]['action'] == 'merge':
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = os.path.join(UPLOAD_FOLDER, message.document.file_name)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        user_data[chat_id]['files'].append(file_path)
        bot.reply_to(message, f"Added {message.document.file_name}. Type /done when finished.")

@bot.message_handler(commands=['done'])
def finish_merge(message):
    chat_id = message.chat.id
    files = user_data.get(chat_id, {}).get('files', [])
    if len(files) < 2:
        bot.reply_to(message, "Please upload at least two PDFs to merge.")
        return

    output_path = os.path.join(UPLOAD_FOLDER, f"merged_{chat_id}.pdf")
    merge_pdfs(files, output_path)

    bot.send_document(chat_id, open(output_path, 'rb'))
    bot.reply_to(message, "Your merged PDF is ready!")
    user_data.pop(chat_id)

if __name__ == "__main__":
    bot.polling()
