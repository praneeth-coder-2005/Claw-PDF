# utils/pdf_utils.py

from pdf2docx import Converter

# Function to convert PDF to Word
def convert_pdf_to_word(pdf_path, word_path):
    """
    Convert a PDF file to a Word document.
    
    :param pdf_path: Path to the input PDF file.
    :param word_path: Path to the output Word file.
    """
    try:
        cv = Converter(pdf_path)
        cv.convert(word_path, start=0, end=None)
        cv.close()
        print(f"Conversion of {pdf_path} to {word_path} completed successfully!")
    except Exception as e:
        print(f"Error while converting PDF to Word: {e}")
