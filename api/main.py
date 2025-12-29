#!/usr/bin/env python3
"""
Mythos API - FastAPI service for external access
Provides secure REST API to Mythos system
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv('/opt/mythos/.env')

app = FastAPI(
    title="Mythos API",
    description="Secure API for Mythos System",
    version="1.0.0"
)

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
    mode: str = "db"

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
            "uuid": result[0],
            "username": result[1],
            "soul_canonical_id": result[2],
            "soul_display_name": result[3],
            "telegram_id": result[4]
        }
    
    return None

# Routes
@app.get("/")
async def root():
    return {
        "service": "Mythos API",
        "status": "running",
        "version": "1.0.0"
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
    """
    
    # For now, just echo back
    # We'll add the actual assistant integration next
    return MessageResponse(
        response=f"Echo: {request.message} (mode: {request.mode})",
        mode=request.mode,
        user=request.user_id
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
