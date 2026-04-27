import streamlit as st
import os
import uuid

from extractor import extract_text_from_pdf
from ai_processor import generate_summary_json, chat_with_document
from formatter import dict_to_html, create_pdf

# Set page config
st.set_page_config(
    page_title="AI Document Analyst",
    page_icon="🤖",
    layout="wide"
)

# Premium CSS
st.markdown("""
<style>
    /* Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f7f7f8;
        border-right: 1px solid #e5e5e5;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #e5e5e5;
        background-color: white;
        color: #333;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        border-color: #999;
        background-color: #f0f0f0;
    }
    
    /* Active Chat Button Highlight */
    .active-chat>button {
        background-color: #e5e5e5 !important;
        font-weight: 600;
        border-color: #ccc;
    }
</style>
""", unsafe_allow_html=True)

# Initialize multi-session state
if "sessions" not in st.session_state:
    st.session_state.sessions = {}  # { session_id: { title, messages, extracted_text, pdf_bytes } }
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "use_demo" not in st.session_state:
    st.session_state.use_demo = False

# Sidebar Configuration
with st.sidebar:
    st.title("🤖 Chat Sessions")
    
    # Global demo toggle
    st.session_state.use_demo = st.toggle("🚀 Demo Mode", value=st.session_state.use_demo, help="Mock AI responses for testing.")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_session_id = None
        st.rerun()
        
    st.markdown("---")
    
    # List all chat sessions
    if st.session_state.sessions:
        st.markdown("<div style='font-size: 0.8em; color: #888; margin-bottom: 10px; font-weight: bold;'>RECENT</div>", unsafe_allow_html=True)
        for s_id, s_data in reversed(list(st.session_state.sessions.items())):
            # Add a visual indicator if this is the active session
            btn_container = st.container()
            if s_id == st.session_state.current_session_id:
                btn_container.markdown('<div class="active-chat">', unsafe_allow_html=True)
            
            if btn_container.button(f"📄 {s_data['title']}", key=f"btn_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
                
            if s_id == st.session_state.current_session_id:
                btn_container.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("*No previous chats yet.*")

# Main Chat Interface
if st.session_state.current_session_id is None:
    # --- NEW CHAT VIEW ---
    st.title("What document would you like to analyze today?")
    st.markdown("Upload a PDF to start a new conversation.", unsafe_allow_html=True)
    
    # API Key Check
    if not st.session_state.use_demo:
        if not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "your_gemini_api_key_here":
            st.error("⚠️ Gemini API Key not found in .env! Please add it or enable Demo Mode in the sidebar.")
            st.stop()
            
    uploaded_file = st.file_uploader("Drop your PDF document here...", type=["pdf"], key="new_uploader")
    
    if uploaded_file is not None:
        new_session_id = str(uuid.uuid4())
        
        with st.spinner("📄 Extracting text..."):
            try:
                pdf_bytes_raw = uploaded_file.read()
                extracted_text = extract_text_from_pdf(pdf_bytes_raw)
            except Exception as e:
                st.error(f"Extraction error: {e}")
                st.stop()
                
        with st.spinner("🧠 Generating executive summary..."):
            try:
                summary_data = generate_summary_json(extracted_text, use_demo=st.session_state.use_demo)
                summary_html = dict_to_html(summary_data)
                
                # Try creating the downloadable PDF
                try:
                    pdf_bytes_generated = create_pdf(summary_data)
                except Exception as e:
                    pdf_bytes_generated = None
                    
                # Create the new session
                title = summary_data.get("document_title", uploaded_file.name)
                # Keep it short for the sidebar
                if len(title) > 25:
                    title = title[:22] + "..."
                    
                st.session_state.sessions[new_session_id] = {
                    "title": title,
                    "extracted_text": extracted_text,
                    "pdf_bytes": pdf_bytes_generated,
                    "messages": [
                        {
                            "role": "assistant",
                            "content": summary_html,
                            "is_html": True
                        }
                    ]
                }
                
                st.session_state.current_session_id = new_session_id
                st.rerun()
            except Exception as e:
                st.error(f"AI error: {e}")
                st.stop()

else:
    # --- EXISTING CHAT VIEW ---
    session = st.session_state.sessions[st.session_state.current_session_id]
    
    st.title(session["title"])
    
    # If we successfully generated a PDF summary, allow downloading it
    if session.get("pdf_bytes"):
        st.download_button(
            label="📥 Download Executive Summary (PDF)",
            data=session["pdf_bytes"],
            file_name=f"Summary_{session['title'].replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        st.markdown("---")

    # Display chat messages for this session
    for msg in session["messages"]:
        with st.chat_message(msg["role"]):
            if msg.get("is_html"):
                st.markdown(msg["content"], unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])
                
    # Chat Input
    if prompt := st.chat_input("Ask a question about this document..."):
        # Append user message to current session
        session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Get AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    history_for_ai = [m for m in session["messages"] if not m.get("is_html")]
                    
                    answer = chat_with_document(
                        session["extracted_text"], 
                        history_for_ai[:-1], 
                        prompt, 
                        use_demo=st.session_state.use_demo
                    )
                    st.markdown(answer)
                    session["messages"].append({"role": "assistant", "content": answer, "is_html": False})
                except Exception as e:
                    st.error(f"Error: {e}")
