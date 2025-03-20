import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

MODEL = "gemini-1.5-flash"

def change_model(name):
    global MODEL
    if name in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        MODEL = name
        return True
    return False

def get_gemini_response(prompt):
    try:
        model_instance = genai.GenerativeModel(MODEL)
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini error: {e}"
