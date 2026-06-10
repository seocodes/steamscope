import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def format_context_to_json(context):
    if isinstance(context, str):
        return context
    return json.dumps(context, indent=2)

def validate_api_key():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")


def build_prompt(context_json):
    prompt = f"""
    You are SteamScope, a Steam deal analyst.
    
    Evaluate the current game price against the historical price data provided in the JSON.
    
    Consider:
    - current price
    - historical lows
    - discount frequency
    - recent price trends
    
    Return a concise JSON response with:
    {{
      "verdict": "excellent|good|fair|poor",
      "summary": "...",
      "confidence": 0,
      "key_insights": []
    }}
    
    Only use information present in the provided JSON.

    Context JSON:
    {context_json}
    """
    return prompt

def parse_gemini_response(response_text):
    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.removeprefix("```json").removesuffix("```").strip()
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```").removesuffix("```").strip()
        
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        return {
                      "verdict": "unknown",
                      "summary": response_text,
                      "confidence": 0,
                      "key_insights": [],
                  }

def analyze_deal(context):
    validate_api_key()
    context_json = format_context_to_json(context)
    prompt = build_prompt(context_json)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return parse_gemini_response(response.text)
