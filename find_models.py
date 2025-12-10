import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: API Key not found.")
    exit()

genai.configure(api_key=api_key)# type: ignore

print("--- AVAILABLE MODELS FOR YOUR KEY ---")
try:
    for m in genai.list_models():# type: ignore
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")