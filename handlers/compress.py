import fitz  # PyMuPDF

def compress_pdf(input_path, output_path):
    """
    Compresses a PDF file to reduce its size.
    
    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to save the compressed PDF.
    
    Returns:
        str: Path to the compressed PDF.
    """
    doc = fitz.open(input_path)
    doc.save(output_path, deflate=True)
    doc.close()
    return output_path
