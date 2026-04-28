import fitz  # PyMuPDF
import io
import csv
from docx import Document

def extract_text_from_file(file_bytes: bytes, file_name: str) -> str:
    """
    Extracts text from a given file byte stream based on its extension.
    Supported extensions: .pdf, .docx, .txt, .csv
    """
    ext = file_name.lower().split('.')[-1]
    
    if ext == 'pdf':
        return _extract_pdf(file_bytes)
    elif ext == 'docx':
        return _extract_docx(file_bytes)
    elif ext in ['txt', 'csv']:
        return _extract_text_or_csv(file_bytes)
    else:
        raise ValueError(f"Unsupported file extension: .{ext}")

def _extract_pdf(pdf_bytes: bytes) -> str:
    text = []
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            if page_text.strip():
                text.append(f"--- PAGE {page_num + 1} ---\n{page_text}")
        return "\n\n".join(text)
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def _extract_docx(docx_bytes: bytes) -> str:
    try:
        doc = Document(io.BytesIO(docx_bytes))
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")

def _extract_text_or_csv(file_bytes: bytes) -> str:
    try:
        # Try decoding with utf-8 first
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1
            return file_bytes.decode('latin-1')
        except Exception as e:
            raise Exception(f"Failed to decode text file: {str(e)}")
