# DocuChat AI

A premium, ChatGPT-style web application that allows users to upload various documents, instantly generates structured executive summaries, and provides an interactive interface to ask follow-up questions about the document's contents.

## Features
- **Universal File Support**: Seamlessly upload and extract text from `.pdf`, `.docx`, `.txt`, and `.csv` files.
- **Multi-Session Memory**: Remember and instantly switch between multiple different documents and chat histories using the sidebar.
- **Premium SaaS UI**: Features a custom theme-aware design (Dark/Light mode) with beautiful typography, gradient accents, pill tags, and sleek chat bubbles.
- **Streaming AI Responses**: Real-time streaming generator so answers type out instantly without long loading times.
- **AI Executive Summary**: Automatically extracts the document title, an executive summary, key themes, and detailed takeaways using the high-performance **Google Gemma 3** model.
- **PDF Export**: Download a beautifully formatted copy of the initial executive summary.
- **Chat Log Export**: Download your entire conversation history with a document as a text file.
- **Demo Mode**: Built-in toggle to use mock data and bypass the AI, perfect for UI testing or avoiding API rate limits.

## Architecture
- **Frontend Engine**: Streamlit with custom CSS and native `.streamlit/config.toml` theming.
- **Document Extraction**: `PyMuPDF` (PDFs), `python-docx` (Word Documents), and standard `io` (TXT/CSV).
- **AI Backend**: Google GenAI SDK (`gemma-3-1b-it`).
- **PDF Generation**: `FPDF2` for rendering clean exportable reports.

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
   Create a `.env` file in the root directory and insert your Google AI Studio API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

Start the Streamlit application:
```bash
streamlit run app.py
```

Upload a document in the main window to automatically generate your summary and begin chatting!
