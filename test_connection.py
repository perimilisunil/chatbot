import google.generativeai as genai # type: ignore
import os
from dotenv import load_dotenv

# 1. Load Environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("--- TESTING GEMINI CONNECTION ---")

# 2. Check Key Existence
if not api_key:
    print("❌ ERROR: API Key not found in .env file.")
    exit()

print(f"✓ API Key found (starts with: {api_key[:5]}...)")

# 3. Configure
try:
    genai.configure(api_key=api_key) # type: ignore
    print("✓ Configuration successful")
except Exception as e:
    print(f"❌ CONFIG ERROR: {e}")
    exit()

# 4. Test Generation
try:
    print("... Contacting Google AI ...")
    model = genai.GenerativeModel('gemini-1.5-flash') # type: ignore
    response = model.generate_content("Reply with the word 'Success'")
    print(f"✓ RESPONSE RECEIVED: {response.text}")
except Exception as e:
    print(f"❌ GENERATION ERROR: {e}")
    print("\nSUGGESTION: Try changing the model name to 'gemini-pro'")