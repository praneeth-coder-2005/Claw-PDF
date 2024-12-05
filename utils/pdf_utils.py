# utils/pdf_utils.py

from pdf2docx import Converter

def convert_pdf_to_word(pdf_path, word_path):
    try:
        cv = Converter(pdf_path)
        cv.convert(word_path, start=0, end=None)
        cv.close()
        print(f"Conversion of {pdf_path} to {word_path} completed successfully!")
    except Exception as e:
        print(f"Error while converting PDF to Word: {e}")
