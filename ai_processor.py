import json
import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SYSTEM_PROMPT = """
You are an expert document analyst.
You will receive raw text extracted from a document.
Your job is to read it carefully, synthesize the most important information, and return ONLY a valid JSON object.

Extract the following fields (use null if not found or not applicable):
- document_title (str: infer a concise title if not explicitly stated)
- executive_summary (str: a concise 1-2 paragraph overview of the entire document)
- key_themes (list of str: 3-5 main themes or topics discussed)
- detailed_points (list of str: 5-10 key takeaways or important details)

Return ONLY the JSON. No explanation. No markdown.
"""

def generate_summary_demo() -> dict:
    """
    Returns a hardcoded summary response after a short delay to simulate AI processing.
    """
    time.sleep(3) # Simulate AI processing time
    
    return {
      "document_title": "Q3 Market Research & Strategy Report",
      "executive_summary": "This document outlines the strategic initiatives and market analysis for Q3. It highlights a significant shift in consumer behavior towards digital-first engagement and recommends reallocating the marketing budget to capitalize on emerging social platforms. Despite supply chain headwinds, the company is well-positioned for double-digit growth if execution aligns with the proposed timeline.",
      "key_themes": [
        "Digital Transformation",
        "Consumer Behavior Shifts",
        "Supply Chain Resilience",
        "Budget Reallocation"
      ],
      "detailed_points": [
        "Mobile traffic has increased by 45% year-over-year, necessitating a mobile-first UI redesign.",
        "Competitor market share in the EMEA region dropped by 5%, opening an expansion window.",
        "Raw material costs are projected to stabilize in late October.",
        "Customer acquisition cost (CAC) on traditional channels has peaked, making influencer partnerships more viable.",
        "The new AI-driven product recommendation engine increased average order value by 12% in beta testing."
      ]
    }

def generate_summary_json(extracted_text: str, use_demo: bool = False) -> dict:
    """
    Sends the extracted PDF text to Gemini API to structure into a JSON Document Summary.
    
    Args:
        extracted_text (str): The raw text extracted from the PDF.
        use_demo (bool): If True, returns a mock response without calling the API.
        
    Returns:
        dict: A dictionary containing the structured document summary.
    """
    if use_demo:
        return generate_summary_demo()
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Gemini API Key is missing. Please set it in the .env file.")

    client = genai.Client(api_key=api_key)

    try:
        prompt = f"Please process the following document text and extract the required information as JSON:\n\n<document>\n{extracted_text}\n</document>"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json"
            )
        )
        content = response.text.strip()
        
        return json.loads(content)

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON. Response was: {content}")
    except Exception as e:
        raise Exception(f"AI Processing failed: {str(e)}")

def chat_with_document(extracted_text: str, chat_history: list, new_message: str, use_demo: bool = False) -> str:
    """
    Sends a follow-up question to Gemini about the document.
    """
    if use_demo:
        time.sleep(2)
        return "*(Demo Mode)* This is a simulated response to your question: '" + new_message + "'. In production, the AI will analyze the document and provide a real answer here!"
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Gemini API Key is missing. Please set it in the .env file.")

    client = genai.Client(api_key=api_key)

    try:
        # Build conversation history
        # Gemini API expects contents to be a string or a list of parts
        # For simplicity in this single-turn emulation, we'll construct a prompt with the history
        
        history_text = ""
        if chat_history:
            history_text = "Previous Conversation History:\n"
            for msg in chat_history:
                role = "User" if msg["role"] == "user" else "AI"
                history_text += f"{role}: {msg['content']}\n"
                
        prompt = f"""You are an expert document assistant. You are helping the user understand a document.
Here is the document text:
<document>
{extracted_text}
</document>

{history_text}

User's new question: {new_message}
Please provide a helpful, accurate, and concise answer based ONLY on the document text.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()

    except Exception as e:
        raise Exception(f"AI Chat failed: {str(e)}")
