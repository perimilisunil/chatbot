from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from utils.db_handler import init_db, get_analytics, get_all_logs,delete_chat_log,get_chat_history
from utils.ai_handler import get_ai_response
from utils.rag_engine import add_document_to_knowledge, get_all_documents, delete_document_by_id
import os
import uuid
import pypdf
import io
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

# Initialize Database
init_db()

# --- Middleware ---
@app.before_request
def assign_session():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
# NEW ROUTE: Fetch History for the Chat Interface
@app.route('/api/history', methods=['GET'])
def get_history_api():
    session_id = session.get('user_id')
    # Get last 50 messages
    history = get_chat_history(session_id, limit=50)# type: ignore
    
    # Convert database rows to JSON list
    # The history comes oldest -> newest, which is perfect for chat
    json_history = []
    for row in history:
        json_history.append({
            'role': row['role'],
            'content': row['content']
        })
        
    return jsonify(json_history)
# --- Routes ---
@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    # Safe JSON retrieval
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    user_message = data['message']
    session_id = session.get('user_id')
    
    # Get Response from AI Handler
    bot_response = get_ai_response(session_id, user_message)
    return jsonify({'response': bot_response})

# --- Admin Routes ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.getenv("ADMIN_PASSWORD", "admin123"):
            session['is_admin'] = True
            return redirect('/admin/dashboard')
        else:
            return "Invalid Password", 401
    return render_template('login.html')

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('is_admin'):
        return redirect('/admin/login')
        
    stats = get_analytics()
    logs = get_all_logs()
    
    # NEW: Fetch what the bot knows
    knowledge = get_all_documents()
    
    return render_template('dashboard.html', stats=stats, logs=logs, knowledge=knowledge)
@app.route('/admin/delete_knowledge/<doc_id>', methods=['POST'])
def delete_knowledge(doc_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    delete_document_by_id(doc_id)
    return redirect('/admin/dashboard')
@app.route('/admin/upload', methods=['POST'])
def upload_knowledge():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 1. Handle Text Input
    text = request.form.get('knowledge_text', '')
    
    # 2. Handle PDF Input (THE FIX)
    if 'pdf_file' in request.files:
        file = request.files['pdf_file']
        
        # Check if user actually selected a file
        if file.filename != '':
            try:
                # FIX: Read file bytes into memory first
                # This prevents "Empty File" or "File Pointer" errors
                file_stream = io.BytesIO(file.read())
                
                # Pass the memory stream to pypdf
                pdf_reader = pypdf.PdfReader(file_stream)
                
                pdf_text = ""
                for page in pdf_reader.pages:
                    # Extract text and handle NoneTypes
                    page_content = page.extract_text()
                    if page_content:
                        pdf_text += page_content + "\n"
                
                print(f"DEBUG: Extracted {len(pdf_text)} characters from PDF.")
                
                # Append PDF text to existing text
                if pdf_text:
                    text = (text or "") + "\n\n--- PDF CONTENT ---\n" + pdf_text

            except Exception as e:
                print(f"❌ PDF Error: {e}")
                return f"Error reading PDF: {str(e)}", 500

    # 3. Save to RAG
    if text and text.strip():
        success = add_document_to_knowledge(text)
        if success:
            return redirect('/admin/dashboard')
        else:
            return "Failed to save to database.", 500
    
    return "No content provided (Text or PDF required)", 400
@app.route('/admin/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    # Import the delete function we just made
    from utils.db_handler import delete_chat_log 
    delete_chat_log(log_id)
    
    return redirect('/admin/dashboard')
if __name__ == '__main__':
    print("--- SERVER STARTED ON http://127.0.0.1:5000 ---")
    app.run(debug=True, port=5000)
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"❌ SERVER CRASHED: {e}")
        input("Press Enter to close...") # Keeps window open on crash