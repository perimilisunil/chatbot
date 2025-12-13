import os
from dotenv import load_dotenv

# Get current folder path
current_path = os.getcwd()
env_path = os.path.join(current_path, ".env")

print(f"--- DEBUGGING API KEY ---")
print(f"1. Looking for .env file at: {env_path}")

if os.path.exists(env_path):
    print("   ✅ File exists!")
else:
    print("   ❌ File NOT found. Check file name and location.")

# Load variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"2. Reading 'GEMINI_API_KEY'...")
if not api_key:
    print("   ❌ Key is Empty or None.")
else:
    print(f"   ✅ Key found! Starts with: {api_key[:5]}...")