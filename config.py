import os

# Telegram Bot Token (replace with your token or use Render ENV vars)
API_TOKEN = os.getenv("API_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# Folder for temporary file uploads
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
