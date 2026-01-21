#!/usr/bin/env python3
"""
Mythos API - FastAPI service with real assistant integration
"""

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from neo4j import GraphDatabase

import json

from media_routes import *

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

# Load environment variables
load_dotenv('/opt/mythos/.env')

app = FastAPI(
    title="Mythos API",
    description="Secure API for Mythos System",
    version="1.1.0"
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

# Neo4j connection for conversation tracking
neo4j_driver = None
try:
    neo4j_driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
    )
    neo4j_driver.verify_connectivity()
    print("✅ Neo4j connected for conversation tracking")
except Exception as e:
    print(f"⚠️  Neo4j connection failed: {e}")

# Request/Response Models
class MessageRequest(BaseModel):
    user_id: str
    message: str
    mode: str = "db"
    model_preference: str = "auto"
    conversation_id: Optional[str] = None  # For tracked conversations

class MessageResponse(BaseModel):
    response: str
    mode: str
    user: Optional[str] = None
    exchange_id: Optional[str] = None  # Returned when in conversation mode

class UserInfo(BaseModel):
    telegram_id: Optional[int] = None
    username: str
    soul_name: str
    uuid: str

class ConversationStartRequest(BaseModel):
    user_id: str
    conversation_id: str
    title: Optional[str] = None

class ConversationEndRequest(BaseModel):
    user_id: str
    conversation_id: str

class ConversationResponse(BaseModel):
    conversation_id: str
    status: str
    exchange_count: Optional[int] = None

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

def extract_keywords(text):
    """Extract meaningful keywords from user's question"""
    stopwords = {'what', 'how', 'when', 'where', 'who', 'why', 'are', 'is', 'the', 'a', 'an', 'me', 'about', 'tell', 'show', 'get', 'find'}
    words = text.lower().split()
    keywords = [w.strip('?.,!') for w in words if w.lower() not in stopwords and len(w) > 3]
    
    phrases = []
    words_clean = [w.strip('?.,!') for w in words]
    for i in range(len(words_clean) - 1):
        phrase = f"{words_clean[i]} {words_clean[i+1]}"
        if len(phrase) > 8:
            phrases.append(phrase)
    
    return keywords + phrases

def get_recent_conversation(user_uuid, conversation_id, limit=5):
    """Get last N messages for immediate context"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT role, content, created_at
            FROM chat_messages
            WHERE user_uuid = %s 
            AND conversation_id = %s
            AND created_at > NOW() - INTERVAL '10 minutes'
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_uuid, conversation_id, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        if not messages:
            return None
        
        messages.reverse()
        context_lines = []
        for role, content, created_at in messages:
            content_short = content[:200] + "..." if len(content) > 200 else content
            context_lines.append(f"{role}: {content_short}")
        
        return "\n".join(context_lines)
    except Exception as e:
        print(f"Error getting recent conversation: {e}")
        conn.close()
        return None

def search_past_conversations(user_uuid, keywords, limit=5):
    """Search all past conversations for topic mentions"""
    if not keywords:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        keyword_conditions = " OR ".join([f"content ILIKE %s" for _ in keywords])
        keyword_params = [f"%{kw}%" for kw in keywords]
        
        cursor.execute(f"""
            SELECT conversation_id, role, content, created_at
            FROM chat_messages
            WHERE user_uuid = %s
            AND ({keyword_conditions})
            AND created_at < NOW() - INTERVAL '1 hour'
            ORDER BY created_at DESC
            LIMIT %s
        """, [user_uuid] + keyword_params + [limit])
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return None
        
        references = []
        for conv_id, role, content, created_at in results:
            date_str = created_at.strftime('%B %d, %Y at %H:%M')
            snippet = content[:150] + "..." if len(content) > 150 else content
            references.append(f"[{date_str}] {role}: {snippet}")
        
        return "\n".join(references)
    except Exception as e:
        print(f"Error searching past conversations: {e}")
        conn.close()
        return None

# Neo4j conversation functions
def create_conversation_node(conversation_id: str, user_id: str, title: str = None):
    """Create a Conversation node in Neo4j"""
    if not neo4j_driver:
        return False
    
    try:
        with neo4j_driver.session() as session:
            session.run("""
                CREATE (c:Conversation {
                    conversation_id: $conversation_id,
                    user_id: $user_id,
                    title: $title,
                    started_at: datetime(),
                    status: 'active',
                    visibility: 'public'
                })
            """, conversation_id=conversation_id, user_id=user_id, title=title)
        return True
    except Exception as e:
        print(f"Error creating conversation node: {e}")
        return False

def create_exchange_node(conversation_id: str, exchange_id: str, sequence: int, 
                         user_message: str, llm_response: str, model_used: str):
    """Create an Exchange node and link to Conversation"""
    if not neo4j_driver:
        return False
    
    try:
        with neo4j_driver.session() as session:
            # Create exchange and link to conversation
            session.run("""
                MATCH (c:Conversation {conversation_id: $conversation_id})
                CREATE (e:Exchange {
                    exchange_id: $exchange_id,
                    sequence: $sequence,
                    timestamp: datetime(),
                    user_message: $user_message,
                    llm_response: $llm_response,
                    model_used: $model_used,
                    visibility: c.visibility
                })
                CREATE (c)-[:CONTAINS]->(e)
            """, 
                conversation_id=conversation_id,
                exchange_id=exchange_id,
                sequence=sequence,
                user_message=user_message,
                llm_response=llm_response,
                model_used=model_used
            )
            
            # Link to previous exchange if exists
            if sequence > 1:
                session.run("""
                    MATCH (c:Conversation {conversation_id: $conversation_id})-[:CONTAINS]->(prev:Exchange {sequence: $prev_seq})
                    MATCH (c)-[:CONTAINS]->(curr:Exchange {sequence: $curr_seq})
                    CREATE (prev)-[:FOLLOWED_BY]->(curr)
                """, conversation_id=conversation_id, prev_seq=sequence-1, curr_seq=sequence)
        
        return True
    except Exception as e:
        print(f"Error creating exchange node: {e}")
        return False

def end_conversation_node(conversation_id: str):
    """Mark conversation as ended and return exchange count"""
    if not neo4j_driver:
        return 0
    
    try:
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (c:Conversation {conversation_id: $conversation_id})
                SET c.status = 'ended', c.ended_at = datetime()
                WITH c
                OPTIONAL MATCH (c)-[:CONTAINS]->(e:Exchange)
                RETURN count(e) as exchange_count
            """, conversation_id=conversation_id)
            
            record = result.single()
            return record["exchange_count"] if record else 0
    except Exception as e:
        print(f"Error ending conversation: {e}")
        return 0

def get_exchange_count(conversation_id: str):
    """Get current exchange count for a conversation"""
    if not neo4j_driver:
        return 0
    
    try:
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (c:Conversation {conversation_id: $conversation_id})-[:CONTAINS]->(e:Exchange)
                RETURN count(e) as count
            """, conversation_id=conversation_id)
            
            record = result.single()
            return record["count"] if record else 0
    except Exception as e:
        print(f"Error getting exchange count: {e}")
        return 0

def get_conversation_context(conversation_id: str, limit: int = 5):
    """Get recent exchanges from Neo4j for context injection"""
    if not neo4j_driver:
        return None
    
    try:
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (c:Conversation {conversation_id: $conversation_id})-[:CONTAINS]->(e:Exchange)
                RETURN e.user_message as user_msg, e.llm_response as llm_msg, e.sequence as seq
                ORDER BY e.sequence DESC
                LIMIT $limit
            """, conversation_id=conversation_id, limit=limit)
            
            exchanges = list(result)
            if not exchanges:
                return None
            
            # Reverse to chronological order
            exchanges.reverse()
            
            context_lines = []
            for record in exchanges:
                user_short = record["user_msg"][:200] + "..." if len(record["user_msg"]) > 200 else record["user_msg"]
                llm_short = record["llm_msg"][:200] + "..." if len(record["llm_msg"]) > 200 else record["llm_msg"]
                context_lines.append(f"User: {user_short}")
                context_lines.append(f"Assistant: {llm_short}")
            
            return "\n".join(context_lines)
    except Exception as e:
        print(f"Error getting conversation context: {e}")
        return None

# Initialize assistants
db_manager_instance = None
if DB_MANAGER_AVAILABLE:
    try:
        db_manager_instance = DatabaseManager()
        print("✅ Database Manager initialized")
    except Exception as e:
        print(f"❌ Error initializing Database Manager: {e}")

# Routes
@app.get("/")
async def root():
    return {
        "service": "Mythos API",
        "status": "running",
        "version": "1.1.0",
        "assistants": {
            "db_manager": DB_MANAGER_AVAILABLE and db_manager_instance is not None,
            "seraphe_assistant": False,
            "genealogy_assistant": False
        },
        "neo4j_connected": neo4j_driver is not None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/conversation/start", response_model=ConversationResponse)
async def start_conversation(
    request: ConversationStartRequest,
    api_key: str = Depends(verify_api_key)
):
    """Start a new tracked conversation"""
    
    user = get_user_by_identifier(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = create_conversation_node(
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        title=request.title
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create conversation in graph")
    
    return ConversationResponse(
        conversation_id=request.conversation_id,
        status="active"
    )

@app.post("/conversation/end", response_model=ConversationResponse)
async def end_conversation(
    request: ConversationEndRequest,
    api_key: str = Depends(verify_api_key)
):
    """End a tracked conversation"""
    
    exchange_count = end_conversation_node(request.conversation_id)
    
    return ConversationResponse(
        conversation_id=request.conversation_id,
        status="ended",
        exchange_count=exchange_count
    )

@app.post("/message", response_model=MessageResponse)
async def process_message(
    request: MessageRequest,
    api_key: str = Depends(verify_api_key)
):
    """Process a message with conversation context"""
    start_time = time.time()
    
    user = get_user_by_identifier(request.user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Use provided conversation_id or generate daily one
    if request.conversation_id:
        conversation_id = request.conversation_id
        # Get context from Neo4j graph
        recent_context = get_conversation_context(conversation_id, limit=5)
    else:
        conversation_id = f"tg-{request.user_id}-{datetime.now().strftime('%Y%m%d')}"
        # Get context from PostgreSQL
        recent_context = get_recent_conversation(user['uuid'], conversation_id, limit=5)
    
    keywords = extract_keywords(request.message)
    historical_context = search_past_conversations(user['uuid'], keywords, limit=3)
    
    # Log incoming user message to PostgreSQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (
                user_uuid, telegram_user_id, conversation_id,
                role, content, mode, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            user['uuid'],
            user.get('telegram_id'),
            conversation_id,
            'user',
            request.message,
            request.mode
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging user message: {e}")
    
    response_text = None
    error_message = None
    cypher_generated = None
    sql_generated = None
    
    try:
        if request.mode == "db" and db_manager_instance:
            db_manager_instance.set_user(user)
            response_text = db_manager_instance.query(
                request.message,
                recent_context=recent_context,
                historical_context=historical_context
            )
            
            if "⚡ Cypher:" in response_text or "⚡️ Cypher:" in response_text:
                lines = response_text.split("\n")
                for i, line in enumerate(lines):
                    if ("⚡ Cypher:" in line or "⚡️ Cypher:" in line) and i + 1 < len(lines):
                        cypher_generated = lines[i + 1].strip()
                        break
            elif "⚡ SQL:" in response_text or "⚡️ SQL:" in response_text:
                lines = response_text.split("\n")
                for i, line in enumerate(lines):
                    if ("⚡ SQL:" in line or "⚡️ SQL:" in line) and i + 1 < len(lines):
                        sql_generated = lines[i + 1].strip()
                        break
        
        elif request.mode == "chat":
            # Pure chat mode - just talk to Ollama
            from ollama import Client
            ollama_client = Client(host=os.getenv('OLLAMA_HOST'))
            
            # Build context-aware prompt
            chat_prompt = ""
            if recent_context:
                chat_prompt += f"Recent conversation:\n{recent_context}\n\n"
            if historical_context:
                chat_prompt += f"Relevant past discussions:\n{historical_context}\n\n"
            chat_prompt += f"User: {request.message}\n\nAssistant:"
            
            ollama_response = ollama_client.generate(
                model=os.getenv('OLLAMA_MODEL', 'qwen2.5:32b'),
                prompt=chat_prompt
            )
            response_text = ollama_response['response'].strip()
        
        elif request.mode == "seraphe":
            response_text = "Seraphe's assistant is not yet connected. Coming soon!"
        
        else:
            response_text = f"Mode '{request.mode}' not yet implemented. Echo: {request.message}"
    
    except Exception as e:
        error_message = str(e)
        response_text = f"❌ Error: {error_message}"
    
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Log assistant response to PostgreSQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (
                user_uuid, telegram_user_id, conversation_id,
                role, content, mode, model_used,
                cypher_generated, sql_generated,
                response_time_ms, error_message,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            user['uuid'],
            user.get('telegram_id'),
            conversation_id,
            'assistant',
            response_text,
            request.mode,
            'qwen2.5:32b',
            cypher_generated,
            sql_generated,
            response_time_ms,
            error_message
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging assistant response: {e}")
    
    # If in tracked conversation mode, create Exchange node in Neo4j
    exchange_id = None
    if request.conversation_id and neo4j_driver:
        exchange_id = f"exchange-{uuid.uuid4()}"
        sequence = get_exchange_count(request.conversation_id) + 1
        create_exchange_node(
            conversation_id=request.conversation_id,
            exchange_id=exchange_id,
            sequence=sequence,
            user_message=request.message,
            llm_response=response_text,
            model_used='qwen2.5:32b'
        )
    
    return MessageResponse(
        response=response_text,
        mode=request.mode,
        user=user['soul_display_name'],
        exchange_id=exchange_id
    )

@app.get("/plaid/callback", response_class=HTMLResponse)
@app.post("/plaid/callback", response_class=HTMLResponse)
async def plaid_callback(request: Request):
    """
    Handle Plaid Link OAuth callback
    This receives the public_token after successful bank linking
    """
    # Get query parameters
    params = dict(request.query_params)
    
    # Check if we have a public_token
    if 'public_token' in params:
        public_token = params['public_token']
        
        # Store token temporarily (you could also write to a file or Redis)
        # For now, we'll just log it and return success
        print(f"✅ Plaid public_token received: {public_token[:20]}...")
        
        # Return success HTML
        return """
        <html>
        <head>
            <title>Bank Linked!</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; background: #f0f0f0; }
                .success { color: #10b981; font-size: 48px; margin-bottom: 20px; }
                h1 { color: #333; }
                p { color: #666; font-size: 18px; }
                .token { 
                    background: #fff; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 20px auto; 
                    max-width: 600px;
                    word-break: break-all;
                    font-family: monospace;
                    border: 2px solid #10b981;
                }
            </style>
        </head>
        <body>
            <div class="success">✓</div>
            <h1>Bank Successfully Linked!</h1>
            <p>Your public token has been received.</p>
            <div class="token">
                <strong>Public Token:</strong><br>
                """ + public_token + """
            </div>
            <p>Copy this token and paste it into your terminal.</p>
            <p style="margin-top: 40px; color: #999;">You can close this window.</p>
        </body>
        </html>
        """
    
    # Handle OAuth state (initial redirect)
    elif 'oauth_state_id' in params:
        return """
        <html>
        <head>
            <title>Processing...</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; }
            </style>
        </head>
        <body>
            <h1>Processing Bank Connection...</h1>
            <p>Please wait while we complete the linking process.</p>
        </body>
        </html>
        """
    
    # Error case
    else:
        return """
        <html>
        <head>
            <title>Error</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; }
                .error { color: #ef4444; }
            </style>
        </head>
        <body>
            <h1 class="error">Error Linking Bank</h1>
            <p>No public token received. Please try again.</p>
        </body>
        </html>
        """

@app.get("/plaid/link", response_class=HTMLResponse)
async def plaid_link_page():
    """
    Serve Plaid Link initialization page
    """
    # Import here to avoid issues if not installed
    from plaid.api import plaid_api
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode
    import plaid
    from plaid.api_client import ApiClient
    from plaid.configuration import Configuration
    from datetime import datetime
    
    PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
    PLAID_SECRET = os.getenv('PLAID_SECRET')
    REDIRECT_URI = 'https://mythos-api.denkers.co/plaid/callback'
    
    # Create Plaid client
    configuration = Configuration(
        host='https://production.plaid.com',
        api_key={
            'clientId': PLAID_CLIENT_ID,
            'secret': PLAID_SECRET,
        }
    )
    
    api_client = ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    
    # Create link token
    try:
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Mythos Finance",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id='user-' + datetime.now().strftime('%Y%m%d%H%M%S')
            ),
            redirect_uri=REDIRECT_URI
        )
        
        response = client.link_token_create(request)
        link_token = response['link_token']
    except Exception as e:
        return f"<h1>Error creating link token</h1><p>{str(e)}</p>"
    
    # Return HTML with Plaid Link
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Mythos Finance - Link Bank</title>
    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 50px;
            text-align: center;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .button {{
            background: #10b981;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s;
        }}
        .button:hover {{
            background: #059669;
        }}
        .token-display {{
            background: #f0f0f0;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            border: 2px solid #10b981;
            display: none;
        }}
        .instructions {{
            color: #666;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏦 Mythos Finance - Link Bank</h1>
        <p class="instructions">Click the button below to connect your bank account securely via Plaid.</p>
        <button id="link-button" class="button">Connect Bank Account</button>
        
        <div id="token-display" class="token-display">
            <h3>✓ Bank Linked Successfully!</h3>
            <p>Copy this token and paste it into your terminal:</p>
            <div id="token-value"></div>
        </div>
    </div>
    
    <script>
    const linkHandler = Plaid.create({{
        token: '{link_token}',
        onSuccess: (public_token, metadata) => {{
            document.getElementById('token-value').textContent = public_token;
            document.getElementById('token-display').style.display = 'block';
            document.getElementById('link-button').style.display = 'none';
        }},
        onExit: (err, metadata) => {{
            if (err != null) {{
                alert('Error: ' + err);
            }}
        }}
    }});
    
    document.getElementById('link-button').addEventListener('click', () => {{
        linkHandler.open();
    }});
    </script>
</body>
</html>"""

@app.get("/user/{identifier}", response_model=UserInfo)
async def get_user(
    identifier: str,
    api_key: str = Depends(verify_api_key)
):
    """Get user information by Telegram ID or username"""
    
    user = get_user_by_identifier(identifier)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserInfo(
        telegram_id=user.get('telegram_id'),
        username=user['username'],
        soul_name=user['soul_display_name'],
        uuid=user['uuid']
    )
