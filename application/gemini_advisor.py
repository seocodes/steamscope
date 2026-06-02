import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def analyze_deal(context):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    prompt = """
    You are SteamScope, a Steam deal analyst.
    
    Evaluate the current game price against the historical price data provided in the JSON.
    
    Consider:
    - current price
    - historical lows
    - discount frequency
    - recent price trends
    
    Return a concise JSON response with:
    {
      "verdict": "excellent|good|fair|poor",
      "summary": "...",
      "confidence": 0,
      "key_insights": []
    }
    
    Only use information present in the provided JSON.\n
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt + context,
    )
    return response.text
