from PyPDF2 import PdfMerger
import pikepdf

def merge_pdfs(files, output_file):
    merger = PdfMerger()
    for file in files:
        merger.append(file)
    merger.write(output_file)
    merger.close()

def compress_pdf(input_file):
    output_file = input_file.replace(".pdf", "_compressed.pdf")
    with pikepdf.Pdf.open(input_file) as pdf:
        pdf.save(output_file, compress_streams=True)
    return output_file
