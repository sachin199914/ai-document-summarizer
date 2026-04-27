# AI Document Summarizer & Chatbot

A premium web application that allows users to upload PDF documents, instantly generates structured executive summaries, and provides a ChatGPT-like interface to ask follow-up questions about the document's contents.

## Features
- **Multi-Session Chat UI**: Remember and seamlessly switch between multiple documents and chat histories in the sidebar.
- **AI Executive Summary**: Automatically extracts the document title, an executive summary, key themes, and detailed takeaways using the **Google Gemini API**.
- **Interactive Q&A**: Chat natively with your document context to extract deeper insights.
- **PDF Export**: Download a beautifully formatted copy of the initial executive summary.
- **Demo Mode**: Built-in toggle to use mock data for testing and presentations without needing an API key.

## Architecture
- **Streamlit**: Web interface and chat session state management.
- **PyMuPDF**: Robust text extraction from PDFs.
- **Google GenAI (`gemini-2.5-flash`)**: AI language model for summarization and Q&A.
- **FPDF2**: Clean PDF report generation.

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
   Create a `.env` file in the root directory and insert your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

Start the Streamlit application:
```bash
streamlit run app.py
```

Upload a PDF through the sidebar to automatically generate your summary and begin chatting!
