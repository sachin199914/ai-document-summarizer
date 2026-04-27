import fitz  # PyMuPDF
import io

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts all text from a given PDF byte stream.
    
    Args:
        pdf_bytes (bytes): The raw bytes of the PDF file.
        
    Returns:
        str: The extracted text, with pages separated by newlines.
    """
    text = []
    
    # Open the PDF from the byte stream
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
