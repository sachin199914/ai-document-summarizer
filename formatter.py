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
<div style="font-family: sans-serif; max-width: 800px; margin: 0 auto; color: #333;">
<h1 style="border-bottom: 3px solid #2e6c80; padding-bottom: 10px; color: #2e6c80; font-size: 2em;">
    {data.get('document_title', 'Untitled Document')}
</h1>

<p style="color: #666; font-style: italic;">Generated on: {datetime.now().strftime("%B %d, %Y")}</p>

<div style="background-color: #f0f7f9; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 5px solid #2e6c80;">
    <h2 style="margin-top: 0; color: #1e4b59; font-size: 1.4em;">Executive Summary</h2>
    <p style="font-size: 1.1em; line-height: 1.6;">{data.get('executive_summary', 'No summary provided.')}</p>
</div>

<h2 style="color: #2e6c80; border-bottom: 2px solid #eee; padding-bottom: 5px;">Key Themes</h2>
<ul style="line-height: 1.6; font-size: 1.05em;">
"""
    
    themes = data.get('key_themes', [])
    if not themes:
        html += "<li>None identified</li>\n"
    else:
        for theme in themes:
            html += f"<li><strong>{theme}</strong></li>\n"
            
    html += """
</ul>

<h2 style="color: #2e6c80; border-bottom: 2px solid #eee; padding-bottom: 5px; margin-top: 25px;">Detailed Takeaways</h2>
<ul style="line-height: 1.6; font-size: 1.05em;">
"""

    points = data.get('detailed_points', [])
    if not points:
        html += "<li>None identified</li>\n"
    else:
        for point in points:
            html += f"<li style='margin-bottom: 8px;'>{point}</li>\n"
            
    html += "</ul>\n"

    html += "</div>"
    
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
