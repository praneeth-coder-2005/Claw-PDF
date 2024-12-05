# handlers/convert.py

from utils.pdf_utils import convert_pdf_to_word

# Function to handle conversion requests
def register_handlers(update, context):
    # Assuming the update contains the PDF path and desired Word path
    pdf_path = update.message.document.file_id  # Example, change according to actual logic
    word_path = f"/path/to/word/{update.message.document.file_id}.docx"

    # Convert PDF to Word
    convert_pdf_to_word(pdf_path, word_path)
    
    # Send response or handle further logic
    update.message.reply_text(f"Conversion started for {pdf_path}. The result will be saved as {word_path}.")
