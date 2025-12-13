import google.generativeai as genai # type: ignore
import os
from dotenv import load_dotenv
from utils.rag_engine import search_knowledge
from utils.db_handler import get_chat_history, log_message
from textblob import TextBlob
load_dotenv()

# --- Configuration ---
api_key = os.getenv("GEMINI_API_KEY")
model = None

# Configure API safely
if api_key:
    try:
        genai.configure(api_key=api_key) # type: ignore
    except Exception as e:
        print(f"API Config Error: {e}")

# Define System Prompt
SYSTEM_INSTRUCTION = """
You are 'FitBot', a specialized Fitness and Health Assistant.
Your goal is to help users with workouts, nutrition, and general wellness.

RULES:
1. STRICTLY answer only questions related to Fitness, Health, Nutrition, and Anatomy.
2. If the user asks about coding, politics, or general off-topic chat, politely refuse.
3. Use the provided Context to answer if available.
"""

# Initialize Model safely
if api_key:
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION) # type: ignore
    except Exception as e:
        print(f"Model Init Error: {e}")

# --- MAIN FUNCTION (MUST BE AT THE LEFT MARGIN) ---
def get_ai_response(session_id, user_message):
    """
    This function handles the AI logic.
    It MUST be defined at the top level (no spaces before 'def').
    """
    
    # 1. Check if Model is ready
    if not model:
        return "Error: Gemini API Key is missing or invalid. Check your .env file."

    # 2. Save User Message to DB
    blob = TextBlob(user_message)
    user_sentiment = blob.sentiment.polarity # type: ignore
    log_message(session_id, "user", user_message,sentiment=user_sentiment)
    
    # 3. Get RAG Context (Search Fitness Knowledge)
    rag_data = search_knowledge(user_message)
    context_text = "\n".join(rag_data) if rag_data else "No specific documents found."
    
    # 4. Get Chat History from DB
    history_rows = get_chat_history(session_id)
    history_formatted = []
    
    for row in history_rows:
        # Convert DB role to Gemini role
        role = "user" if row.role == "user" else "model"
        history_formatted.append({"role": role, "parts": [{"text": row.content}]})
    
    # 5. Build the Prompt
    full_prompt = f"Context from Knowledge Base:\n{context_text}\n\nUser Question: {user_message}"
    
    # 6. Generate Response
    try:
        # Try snake_case (Modern SDK)
        if hasattr(model, 'start_chat'):
            chat = model.start_chat(history=history_formatted) # type: ignore
            response = chat.send_message(full_prompt) # type: ignore
        # Fallback to camelCase (Old SDK)
        else:
            chat = model.startChat(history=history_formatted) # type: ignore
            response = chat.sendMessage(full_prompt) # type: ignore
            
        ai_text = response.text
    except Exception as e:
        print(f"Gemini Generation Error: {e}")
        ai_text = "I'm having trouble connecting to the AI service right now."
        
    # 7. Save AI Response to DB
    log_message(session_id, "model", ai_text,sentiment=0)
    
    return ai_text