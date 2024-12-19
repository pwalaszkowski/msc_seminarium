from PyPDF2 import PdfReader


def load_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        text.extend(page.extract_text().splitlines())
    return [line.strip() for line in text if line.strip()]

def load_pdf_pages(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        text = ''

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text
