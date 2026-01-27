#!/usr/bin/env python3
"""
Mythos API - FastAPI service with real assistant integration
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys
from dotenv import load_dotenv
from api.routes.sales import router as sales_router
import psycopg2

# Add assistants to path
sys.path.insert(0, '/opt/mythos/assistants')

# Import assistants
try:
    from db_manager import DatabaseManager
    DB_MANAGER_AVAILABLE = True
    print("✅ db_manager imported successfully")
except ImportError as e:
    DB_MANAGER_AVAILABLE = False
    print(f"⚠️  Warning: db_manager not available - {e}")

try:
    from chat_assistant import ChatAssistant
    CHAT_ASSISTANT_AVAILABLE = True
    print("✅ chat_assistant imported successfully")
except ImportError as e:
    CHAT_ASSISTANT_AVAILABLE = False
    print(f"⚠️  Warning: chat_assistant not available - {e}")

# Load environment variables
load_dotenv('/opt/mythos/.env')

app = FastAPI(
    title="Mythos API",
    description="Secure API for Mythos System",
    version="1.1.0"
)

# Include sales router
app.include_router(sales_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key authentication
API_KEYS = {
    os.getenv('API_KEY_TELEGRAM_BOT'): "telegram_bot",
    os.getenv('API_KEY_KA'): "ka",
    os.getenv('API_KEY_SERAPHE'): "seraphe"
}

# Request/Response Models
class MessageRequest(BaseModel):
    user_id: str
    message: str
    mode: str = "chat"  # Default to chat mode now
    model_preference: str = "auto"  # Add model preference
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    mode: str
    user: Optional[str] = None

class UserInfo(BaseModel):
    telegram_id: Optional[int] = None
    username: str
    soul_name: str
    uuid: str

# Authentication
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return API_KEYS[x_api_key]

# Helper functions
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def get_user_by_identifier(identifier: str):
    """Look up user by Telegram ID or username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        telegram_id = int(identifier)
        cursor.execute("""
            SELECT user_uuid, username, soul_canonical_id, soul_display_name, telegram_id
            FROM users
            WHERE telegram_id = %s
        """, (telegram_id,))
    except ValueError:
        cursor.execute("""
            SELECT user_uuid, username, soul_canonical_id, soul_display_name, telegram_id
            FROM users
            WHERE username = %s
        """, (identifier,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "uuid": str(result[0]),
            "username": result[1],
            "soul_canonical_id": result[2],
            "soul_display_name": result[3],
            "telegram_id": result[4]
        }
    
    return None

# Initialize assistants (singleton pattern)
db_manager_instance = None
if DB_MANAGER_AVAILABLE:
    try:
        db_manager_instance = DatabaseManager()
        print("✅ Database Manager initialized")
    except Exception as e:
        print(f"❌ Error initializing Database Manager: {e}")

chat_assistant_instance = None
if CHAT_ASSISTANT_AVAILABLE:
    try:
        chat_assistant_instance = ChatAssistant()
        print("✅ Chat Assistant initialized")
    except Exception as e:
        print(f"❌ Error initializing Chat Assistant: {e}")

# Routes
@app.get("/")
async def root():
    return {
        "service": "Mythos API",
        "status": "running",
        "version": "1.1.0",
        "assistants": {
            "chat_assistant": CHAT_ASSISTANT_AVAILABLE and chat_assistant_instance is not None,
            "db_manager": DB_MANAGER_AVAILABLE and db_manager_instance is not None,
            "seraphe_assistant": False,
            "genealogy_assistant": False
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/message", response_model=MessageResponse)
async def process_message(
    request: MessageRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Process a message through the Mythos system.
    
    Modes:
    - chat: General conversation with Ollama (default)
    - db: Database queries via natural language
    - seraphe: Cosmology assistant (coming soon)
    - genealogy: Bloodline research (coming soon)
    """
    
    # Look up user
    user = get_user_by_identifier(request.user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Route to appropriate assistant based on mode
    
    # CHAT MODE - General conversation
    if request.mode == "chat" and chat_assistant_instance:
        try:
            # Set user context
            chat_assistant_instance.set_user(user)
            
            # Process message with model preference
            response_text = chat_assistant_instance.query(
                request.message,
                model_preference=request.model_preference
            )
            
            return MessageResponse(
                response=response_text,
                mode=request.mode,
                user=user['soul_display_name']
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat assistant error: {str(e)}")
    
    # DB MODE - Database queries
    elif request.mode == "db" and db_manager_instance:
        try:
            # Set user context
            db_manager_instance.set_user(user)
            
            # Process message
            response_text = db_manager_instance.query(request.message)
            
            return MessageResponse(
                response=response_text,
                mode=request.mode,
                user=user['soul_display_name']
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database manager error: {str(e)}")
    
    # SERAPHE MODE - Cosmology assistant
    elif request.mode == "seraphe":
        # Placeholder for Seraphe's assistant
        return MessageResponse(
            response="Seraphe's assistant is not yet connected. Coming soon!",
            mode=request.mode,
            user=user['soul_display_name']
        )
    
    # GENEALOGY MODE - Bloodline research
    elif request.mode == "genealogy":
        return MessageResponse(
            response="Genealogy assistant is not yet connected. Coming soon!",
            mode=request.mode,
            user=user['soul_display_name']
        )
    
    # Fallback for unavailable modes
    else:
        # Check if the mode exists but assistant isn't available
        if request.mode == "chat" and not chat_assistant_instance:
            return MessageResponse(
                response="Chat assistant is not available. Check server logs.",
                mode=request.mode,
                user=user['soul_display_name']
            )
        elif request.mode == "db" and not db_manager_instance:
            return MessageResponse(
                response="Database manager is not available. Check server logs.",
                mode=request.mode,
                user=user['soul_display_name']
            )
        
        # Unknown mode
        return MessageResponse(
            response=f"Mode '{request.mode}' is not recognized. Available modes: chat, db, seraphe, genealogy",
            mode=request.mode,
            user=user['soul_display_name']
        )

@app.get("/user/{identifier}", response_model=UserInfo)
async def get_user(
    identifier: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get user information by Telegram ID or username.
    """
    
    user = get_user_by_identifier(identifier)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserInfo(
        telegram_id=user.get('telegram_id'),
        username=user['username'],
        soul_name=user['soul_display_name'],
        uuid=user['uuid']
    )

@app.post("/chat/clear/{user_id}")
async def clear_chat_context(
    user_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Clear chat context for a user"""
    if not chat_assistant_instance:
        raise HTTPException(status_code=503, detail="Chat assistant not available")
    
    user = get_user_by_identifier(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    chat_assistant_instance.clear_context(user['uuid'])
    
    return {"status": "ok", "message": "Chat context cleared"}

@app.get("/chat/stats/{user_id}")
async def get_chat_stats(
    user_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get chat context statistics for a user"""
    if not chat_assistant_instance:
        raise HTTPException(status_code=503, detail="Chat assistant not available")
    
    user = get_user_by_identifier(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stats = chat_assistant_instance.get_context_stats(user['uuid'])
    
    return {"status": "ok", "stats": stats}
