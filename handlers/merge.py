from PyPDF2 import PdfMerger
import os

def merge_pdfs(files, output_path):
    """
    Merges multiple PDF files into a single PDF.
    
    Args:
        files (list): List of file paths to be merged.
        output_path (str): Output file path.
    
    Returns:
        str: Path to the merged PDF.
    """
    merger = PdfMerger()
    for pdf in files:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()
    return output_path
