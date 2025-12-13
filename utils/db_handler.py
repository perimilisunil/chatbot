import os
from flask import current_app
from flask_sqlalchemy import SQLAlchemy

# 1.  Define SQLAlchemy instance 
db = SQLAlchemy()

def init_db(app):
    """Initializes the database using Flask app context."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
    db.init_app(app)   
    with app.app_context():  
        db.create_all()  
    print("Database initialized.")

# --- MODEL DEFINITIONS (The new way to handle tables) ---
# These are class definitions and must be outside the app context.
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    role = db.Column(db.String(10))
    content = db.Column(db.Text)
    sentiment = db.Column(db.Float, default=0.0)  # Store sentiment
    timestamp = db.Column(db.DateTime, server_default=db.func.now())  # Auto timestamp

# --- Helper Functions (Simplified) ---

def log_message(session_id, role, content, sentiment=0.0):
    """Saves a message with sentiment, using SQLAlchemy."""
    if current_app:
        new_log = ChatLog(session_id=session_id, role=role, content=content, sentiment=sentiment)# type: ignore
        db.session.add(new_log)
        db.session.commit()

def get_chat_history(session_id, limit=10):
    """Retrieves chat history with limit."""
    from flask import current_app # Import inside the function
    with current_app.app_context():
        return ChatLog.query.filter_by(session_id=session_id).order_by(ChatLog.id.desc()).limit(limit).all()

def get_analytics():
    """Gets basic analytics (counts)."""
    from flask import current_app
    with current_app.app_context():
        total_messages = ChatLog.query.count()
        active_users = db.session.query(ChatLog.session_id.distinct()).count()
    return {'total_messages': total_messages, 'active_users': active_users}

def get_sentiment_stats():
    """Calculates the average sentiment."""
    from flask import current_app
    with current_app.app_context():
        avg_sentiment = db.session.query(db.func.avg(ChatLog.sentiment)).filter_by(role='user').scalar()
        if avg_sentiment is None: return "Neutral"
        if avg_sentiment > 0.1: return "Positive"
        if avg_sentiment < -0.1: return "Negative"
        return " Neutral"

def get_all_logs():
    """Fetches all chat logs."""
    from flask import current_app
    with current_app.app_context():
        return ChatLog.query.order_by(ChatLog.id.desc()).limit(50).all()

def delete_chat_log(log_id):
    """Deletes a chat log by its ID."""
    from flask import current_app
    with current_app.app_context():
        log_to_delete = ChatLog.query.get(log_id)
        if log_to_delete:
            db.session.delete(log_to_delete)
            db.session.commit()