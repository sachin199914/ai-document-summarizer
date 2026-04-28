from fpdf import FPDF
from datetime import datetime

def wrap_long_words(text, max_len=60):
    if not text:
        return ""
    text = str(text)
    words = text.split(" ")
    wrapped = []
    for w in words:
        if len(w) > max_len:
            wrapped.append(" ".join([w[i:i+max_len] for i in range(0, len(w), max_len)]))
        else:
            wrapped.append(w)
    return " ".join(wrapped)

class SummaryPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "Document Summary Report", 0, 1, "C")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 13)
        self.set_text_color(46, 108, 128) # #2e6c80
        self.cell(0, 8, wrap_long_words(title), 0, 1, "L")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 6, wrap_long_words(body))
        self.ln(6)
        
    def bullet_list(self, items):
        if not items:
            self.chapter_body("None found.")
            return
            
        self.set_font("Arial", "", 11)
        for item in items:
            # Check if item is a dict (just in case), otherwise stringify
            item_text = wrap_long_words(str(item))
            self.multi_cell(0, 6, f"\x95 {item_text}")
        self.ln(6)

def dict_to_html(data: dict) -> str:
    """
    Converts the structured JSON dictionary into formatted HTML for Streamlit display.
    """
    
    html = f"""
<div style="font-family: inherit; max-width: 780px; margin: 0 auto; padding: 10px 0;">

<h1 style="font-size: 1.8em; font-weight: 700; margin-bottom: 6px; padding-bottom: 14px; border-bottom: 1px solid rgba(128,128,128,0.25);">
    {data.get('document_title', 'Untitled Document')}
</h1>
<p style="opacity: 0.5; font-size: 0.85em; margin-bottom: 28px;">Generated on {datetime.now().strftime("%B %d, %Y")}</p>

<div style="padding: 20px 22px; border-radius: 10px; margin-bottom: 28px; border: 1px solid rgba(128,128,128,0.2); background: rgba(128,128,128,0.08);">
    <h3 style="margin: 0 0 10px 0; font-weight: 600;">📋 Executive Summary</h3>
    <p style="font-size: 1em; line-height: 1.75; margin: 0; opacity: 0.9;">{data.get('executive_summary', 'No summary provided.')}</p>
</div>

<h3 style="font-weight: 600; margin-bottom: 12px;">🏷️ Key Themes</h3>
<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 28px;">
"""
    
    themes = data.get('key_themes', [])
    if not themes:
        html += "<span style='opacity:0.5;'>None identified</span>\n"
    else:
        pill_styles = [
            "background:rgba(99,102,241,0.15); color:#818CF8;",
            "background:rgba(16,185,129,0.15); color:#34D399;",
            "background:rgba(245,158,11,0.15); color:#FBBF24;",
            "background:rgba(239,68,68,0.15); color:#F87171;",
            "background:rgba(168,85,247,0.15); color:#C084FC;",
        ]
        for i, theme in enumerate(themes):
            style = pill_styles[i % len(pill_styles)]
            html += f'<span style="display:inline-block; padding: 5px 14px; border-radius: 50px; font-size: 0.88em; font-weight: 500; {style}">{theme}</span>\n'
            
    html += """
</div>

<h3 style="font-weight: 600; margin-bottom: 12px;">📌 Detailed Takeaways</h3>
<ul style="line-height: 1.75; font-size: 1em; padding-left: 18px; opacity: 0.9;">
"""

    points = data.get('detailed_points', [])
    if not points:
        html += "<li>None identified</li>\n"
    else:
        for point in points:
            html += f"<li style='margin-bottom: 8px;'>{point}</li>\n"
            
    html += "</ul>\n</div>"
    
    return html

def create_pdf(data: dict) -> bytes:
    """
    Generates a PDF byte stream from the structured JSON document summary data.
    """
    pdf = SummaryPDF()
    pdf.add_page()
    
    # Document Title
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(46, 108, 128)
    pdf.multi_cell(0, 10, wrap_long_words(str(data.get('document_title', 'Untitled Document'))))
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%B %d, %Y')}", 0, 1)
    pdf.ln(8)
    
    # Executive Summary
    pdf.chapter_title("Executive Summary")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, wrap_long_words(str(data.get('executive_summary', 'No summary provided.'))))
    pdf.ln(8)
    
    # Key Themes
    pdf.chapter_title("Key Themes")
    themes = data.get("key_themes", [])
    pdf.bullet_list(themes)
    
    # Detailed Points
    pdf.chapter_title("Detailed Takeaways")
    points = data.get("detailed_points", [])
    pdf.bullet_list(points)
        
    return pdf.output(dest='S').encode('latin1')
