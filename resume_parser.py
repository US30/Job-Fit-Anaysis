import PyPDF2
import io

def extract_text_from_pdf(file_bytes):
    """
    Extracts text from a PDF file provided as bytes.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

