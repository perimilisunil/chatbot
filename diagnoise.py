import google.generativeai as genai
import os
from dotenv import load_dotenv

print("--- STARTING DIAGNOSTIC TEST ---")

# TEST 1: Load Environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ FAIL: API Key not found in .env file.")
    print("   -> Fix: Check if .env exists and has GEMINI_API_KEY=... inside.")
    exit()
else:
    print(f"✅ PASS: API Key found (Starts with {api_key[:5]}...)")

# TEST 2: Configure & Check Permissions
try:
    genai.configure(api_key=api_key)# type: ignore
    print("✅ PASS: Configuration successful.")
except Exception as e:
    print(f"❌ FAIL: Configuration crashed. Error: {e}")
    exit()

# TEST 3: Test Chat Model (gemini-1.5-flash)
print("\n--- TESTING CHAT MODEL ---")
try:
    model = genai.GenerativeModel('gemini-2.0-flash')# type: ignore
    response = model.generate_content("Say 'Hello'")
    print(f"✅ PASS: Chat Model works! Reply: {response.text.strip()}")
except Exception as e:
    print(f"❌ FAIL: Chat Model crashed.")
    print(f"   Error Message: {e}")
    print("   -> Fix: Your API key might not support this model, or Quota exceeded.")

# TEST 4: Test Embedding Model (RAG)
print("\n--- TESTING EMBEDDING MODEL (RAG) ---")
try:
    result = genai.embed_content(# type: ignore
        model="models/text-embedding-004",
        content="Test",
        task_type="retrieval_document"
    )
    print("✅ PASS: Embedding Model works!")
except Exception as e:
    print(f"❌ FAIL: Embedding Model crashed.")
    print(f"   Error Message: {e}")
    print("   -> Fix: Your RAG engine will crash the app. You must disable RAG.")