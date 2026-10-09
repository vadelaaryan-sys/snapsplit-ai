"""
ai_service.py - Gemini Vision & Chat interaction handler for SnapSplit
"""

import os
import json
from PIL import Image
from prompts import SYSTEM_PROMPT

def get_gemini_response(api_key: str, image: Image.Image, user_prompt: str, model_name: str = "gemini-2.5-flash"):
    """
    Sends an image + prompt to Gemini Vision API.
    Attempts modern `google-genai` SDK first, then falls back to `google-generativeai`.
    """
    if not api_key:
        raise ValueError("Google Gemini API Key is required. Please set it in secrets or the sidebar.")

    # Method 1: Try modern google-genai SDK
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        
        # Combine system prompt with user instructions
        full_prompt = f"{SYSTEM_PROMPT}\n\nTask:\n{user_prompt}"
        
        response = client.models.generate_content(
            model=model_name,
            contents=[image, full_prompt]
        )
        return response.text
    except Exception as err_modern:
        # Method 2: Fall back to google-generativeai
        try:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            
            # Map model names if needed
            legacy_model_name = "gemini-1.5-flash" if "2.5" in model_name else model_name
            model = genai_legacy.GenerativeModel(legacy_model_name)
            
            full_prompt = f"{SYSTEM_PROMPT}\n\nTask:\n{user_prompt}"
            response = model.generate_content([full_prompt, image])
            return response.text
        except Exception as err_legacy:
            raise RuntimeError(f"Gemini API Error: {str(err_modern)} | Fallback error: {str(err_legacy)}")


def analyze_receipt(api_key: str, image: Image.Image, model_name: str = "gemini-2.5-flash"):
    """
    Analyzes a receipt image and returns structured JSON analysis as well as human readable markdown.
    """
    prompt = """
    Analyze this receipt carefully and return a JSON block followed by a brief markdown summary.
    
    The output MUST strictly contain a JSON block with the following keys inside ```json ``` code fence:
    {
      "merchant": "Merchant or restaurant name",
      "date": "Date if found, or N/A",
      "currency": "$",
      "items": [
        {"name": "Item 1", "quantity": 1, "price": 10.50},
        {"name": "Item 2", "quantity": 2, "price": 8.00}
      ],
      "subtotal": 26.50,
      "tax": 2.12,
      "tip": 4.00,
      "total": 32.62
    }

    After the JSON block, provide a short friendly summary of the receipt contents.
    """
    
    raw_response = get_gemini_response(api_key, image, prompt, model_name)
    
    # Try parsing JSON out of response
    parsed_data = None
    try:
        if "```json" in raw_response:
            json_str = raw_response.split("```json")[1].split("```")[0].strip()
            parsed_data = json.loads(json_str)
        elif "```" in raw_response:
            json_str = raw_response.split("```")[1].split("```")[0].strip()
            parsed_data = json.loads(json_str)
    except Exception:
        pass
        
    return raw_response, parsed_data


def chat_about_receipt(api_key: str, image: Image.Image, chat_history: list, new_question: str, model_name: str = "gemini-2.5-flash"):
    """
    Handles follow-up chat about an uploaded receipt image.
    """
    history_context = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_context += f"{role}: {msg['content']}\n"
        
    prompt = f"""
    Context - Previous Conversation:
    {history_context}
    
    User Question:
    {new_question}
    
    Answer the user's question accurately based on the receipt image.
    """
    
    return get_gemini_response(api_key, image, prompt, model_name)
