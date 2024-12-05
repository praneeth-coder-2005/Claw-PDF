import os

# Telegram API Token (replace with your bot token or use Render ENV vars)
API_TOKEN = os.getenv("API_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# Directory to store uploaded and processed files
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
