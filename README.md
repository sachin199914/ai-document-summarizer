# Deal Memo Generator

A web application that takes a pitch deck or property summary PDF and automatically generates a structured, professionally formatted Investment Memo using Claude AI.

## Architecture
- **Streamlit**: Web interface for PDF upload and memo rendering.
- **PyMuPDF**: Robust text extraction from PDFs.
- **Anthropic Claude**: AI extraction of structured financial and strategic metrics from raw text.
- **FPDF2**: Clean PDF memo generation.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment Variables:
   Edit the `.env` file and insert your Anthropic API key:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03...
   ```

## Usage

Start the Streamlit application:
```bash
streamlit run app.py
```

Upload a PDF through the web interface to automatically generate your investment memo!
