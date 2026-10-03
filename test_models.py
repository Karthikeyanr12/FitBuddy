import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY and API_KEY.strip() and API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=API_KEY.strip())
    print("Testing Gemini API connection...")
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        print(f"Successfully connected! Found {len(available_models)} models supporting generateContent:")
        for name in available_models[:6]:
            print(f" - {name}")
    except Exception as e:
        print(f"API key error: {e}")
else:
    print("No valid GOOGLE_API_KEY set in .env. Using fallback generator mode.")
