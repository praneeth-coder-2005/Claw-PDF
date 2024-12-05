import os

def validate_pdf(file_path):
    return file_path.lower().endswith(".pdf")

def cleanup_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)
