import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

MODEL = "gemini-1.5-flash"

def cambia_modello(nome):
    global MODEL
    if nome in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        MODEL = nome
        return True
    return False

def get_gemini_response(prompt):
    try:
        modello = genai.GenerativeModel(MODEL)
        response = modello.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Errore Gemini: {e}"
