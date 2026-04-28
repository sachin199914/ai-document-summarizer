import streamlit as st
import os
import uuid

from extractor import extract_text_from_file
from ai_processor import generate_summary_json, chat_with_document_stream
from formatter import dict_to_html, create_pdf

# Set page config
st.set_page_config(
    page_title="DocuChat AI",
    page_icon="🤖",
    layout="wide"
)

# ─── Minimal, clean CSS (works with Streamlit's native dark theme) ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, header, footer, .stDeployButton { display: none !important; }

    /* Rounded buttons with subtle glow */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px) !important;
    }

    /* New Chat accent button */
    .new-chat-btn .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
    }
    .new-chat-btn .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(99,102,241,0.55) !important;
        transform: translateY(-2px) !important;
    }

    /* Active chat highlight */
    .active-chat .stButton>button {
        background: rgba(99,102,241,0.15) !important;
        border: 1px solid rgba(99,102,241,0.4) !important;
        color: #A5B4FC !important;
        font-weight: 600 !important;
    }

    /* Chat message entrance animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatMessage {
        animation: fadeIn 0.3s ease-out !important;
        border-radius: 12px !important;
    }

    /* User avatar color */
    [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #059669, #10B981) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── State ───────────────────────────────────────────────────────────────
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "use_demo" not in st.session_state:
    st.session_state.use_demo = False

# ─── Sidebar ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 DocuChat AI")
    
    st.session_state.use_demo = st.toggle("🚀 Demo Mode", value=st.session_state.use_demo, help="Mock AI responses for testing.")
    
    st.markdown("")
    
    nc = st.container()
    nc.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if nc.button("➕  New Chat", use_container_width=True):
        st.session_state.current_session_id = None
        st.rerun()
    nc.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    if st.session_state.sessions:
        st.caption("RECENT CHATS")
        for s_id, s_data in reversed(list(st.session_state.sessions.items())):
            c = st.container()
            is_active = s_id == st.session_state.current_session_id
            if is_active:
                c.markdown('<div class="active-chat">', unsafe_allow_html=True)
            if c.button(f"📄 {s_data['title']}", key=f"btn_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
            if is_active:
                c.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("No chats yet. Upload a document to begin.")

# ─── Main Content ────────────────────────────────────────────────────────
if st.session_state.current_session_id is None:
    # ── Welcome / Upload View ──
    st.markdown("")
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 📄 What would you like to analyze?")
        st.markdown("Upload a document to get an executive summary and chat with it.")
        st.markdown("")
        
        # API Key Check
        if not st.session_state.use_demo:
            if not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "your_gemini_api_key_here":
                st.error("⚠️ Gemini API Key not found in .env! Enable Demo Mode in the sidebar.")
                st.stop()
        
        uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt", "csv"], key="new_uploader")
    
    if uploaded_file is not None:
        new_session_id = str(uuid.uuid4())
        
        with st.spinner("📄 Extracting text..."):
            try:
                file_bytes_raw = uploaded_file.read()
                extracted_text = extract_text_from_file(file_bytes_raw, uploaded_file.name)
            except Exception as e:
                st.error(f"Extraction error: {e}")
                st.stop()
                
        with st.spinner("🧠 Generating executive summary..."):
            try:
                summary_data = generate_summary_json(extracted_text, use_demo=st.session_state.use_demo)
                summary_html = dict_to_html(summary_data)
                
                try:
                    pdf_bytes_generated = create_pdf(summary_data)
                except Exception:
                    pdf_bytes_generated = None
                    
                title = summary_data.get("document_title", uploaded_file.name)
                if len(title) > 28:
                    title = title[:25] + "..."
                    
                st.session_state.sessions[new_session_id] = {
                    "title": title,
                    "extracted_text": extracted_text,
                    "pdf_bytes": pdf_bytes_generated,
                    "messages": [
                        {"role": "assistant", "content": summary_html, "is_html": True}
                    ]
                }
                
                st.session_state.current_session_id = new_session_id
                st.rerun()
            except Exception as e:
                st.error(f"AI error: {e}")
                st.stop()

else:
    # ── Active Chat View ──
    session = st.session_state.sessions[st.session_state.current_session_id]
    
    hdr1, hdr2 = st.columns([3, 1])
    with hdr1:
        st.markdown(f"### {session['title']}")
    with hdr2:
        if session.get("pdf_bytes"):
            st.download_button(
                "📥 Download PDF",
                data=session["pdf_bytes"],
                file_name=f"Summary_{session['title'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # Chat messages
    for msg in session["messages"]:
        with st.chat_message(msg["role"]):
            if msg.get("is_html"):
                st.markdown(msg["content"], unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])
                
    # Chat input
    if prompt := st.chat_input("Ask anything about this document..."):
        session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    history_for_ai = [m for m in session["messages"] if not m.get("is_html")]
                    stream = chat_with_document_stream(
                        session["extracted_text"],
                        history_for_ai[:-1],
                        prompt,
                        use_demo=st.session_state.use_demo
                    )
                    answer = st.write_stream(stream)
                    session["messages"].append({"role": "assistant", "content": answer, "is_html": False})
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    # Export in sidebar
    with st.sidebar:
        st.markdown("---")
        chat_log = f"Chat Log: {session['title']}\n{'='*40}\n\n"
        for msg in session["messages"]:
            role = "USER" if msg["role"] == "user" else "AI"
            content = "(Summary — see web view)" if msg.get("is_html") else msg["content"]
            chat_log += f"[{role}]:\n{content}\n\n"
        st.download_button(
            "⬇️ Export Chat Log",
            data=chat_log,
            file_name=f"ChatLog_{session['title'].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
