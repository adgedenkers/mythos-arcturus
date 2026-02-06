#!/usr/bin/env python3
"""
Mythos API - Google OAuth2 + JWT Authentication
/opt/mythos/api/auth/google_auth.py

Flow:
  1. User visits /auth/google/login
  2. Redirected to Google consent screen
  3. Google redirects back to /auth/google/callback with auth code
  4. We exchange code for user info (email, name)
  5. Check email against web_users whitelist
  6. Issue JWT as httponly cookie
  7. All /app/* and /api/finance/* routes require valid JWT
"""
import os
import json
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Request, HTTPException, Depends, Response
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Google OAuth config
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'https://mythos-api.denkers.co/auth/google/callback')

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# JWT config
JWT_SECRET = os.getenv('JWT_SECRET', '')
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', '168'))  # 7 days default
JWT_COOKIE_NAME = "mythos_session"

# CSRF state storage (in-memory, fine for single-server)
_oauth_states = {}


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def check_whitelist(email: str) -> Optional[dict]:
    """Check if email is in web_users whitelist"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, email, display_name, role, is_active
        FROM web_users
        WHERE email = %s AND is_active = true
    """, (email.lower(),))
    user = cur.fetchone()
    conn.close()
    return dict(user) if user else None


def update_last_login(email: str, google_name: str = None, google_picture: str = None):
    """Update last login timestamp and Google profile info"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE web_users
        SET last_login = NOW(),
            google_name = COALESCE(%s, google_name),
            google_picture = COALESCE(%s, google_picture)
        WHERE email = %s
    """, (google_name, google_picture, email.lower()))
    conn.commit()
    conn.close()


def create_jwt(user: dict) -> str:
    """Create a JWT token for authenticated user"""
    payload = {
        "sub": user['email'],
        "name": user['display_name'],
        "role": user.get('role', 'user'),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(request: Request) -> Optional[dict]:
    """Extract current user from JWT cookie"""
    token = request.cookies.get(JWT_COOKIE_NAME)
    if not token:
        return None
    return verify_jwt(token)


async def require_auth(request: Request) -> dict:
    """Dependency: require authenticated user"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ========== ROUTES ==========

@router.get("/google/login")
async def google_login():
    """Redirect to Google OAuth consent screen"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID in .env")
    
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = datetime.utcnow()
    
    # Clean old states (> 10 min)
    cutoff = datetime.utcnow() - timedelta(minutes=10)
    expired = [k for k, v in _oauth_states.items() if v < cutoff]
    for k in expired:
        del _oauth_states[k]
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle Google OAuth callback"""
    
    if error:
        return RedirectResponse(url=f"/app/login?error={error}")
    
    if not code or not state:
        return RedirectResponse(url="/app/login?error=missing_params")
    
    # Verify state
    if state not in _oauth_states:
        return RedirectResponse(url="/app/login?error=invalid_state")
    del _oauth_states[state]
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    
    if token_response.status_code != 200:
        logger.error(f"Token exchange failed: {token_response.text}")
        return RedirectResponse(url="/app/login?error=token_failed")
    
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    
    if not access_token:
        return RedirectResponse(url="/app/login?error=no_access_token")
    
    # Get user info from Google
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    
    if userinfo_response.status_code != 200:
        return RedirectResponse(url="/app/login?error=userinfo_failed")
    
    google_user = userinfo_response.json()
    email = google_user.get("email", "").lower()
    name = google_user.get("name", "")
    picture = google_user.get("picture", "")
    
    if not email:
        return RedirectResponse(url="/app/login?error=no_email")
    
    # Check whitelist
    web_user = check_whitelist(email)
    if not web_user:
        logger.warning(f"Unauthorized login attempt: {email}")
        return RedirectResponse(url="/app/login?error=unauthorized")
    
    # Update last login
    update_last_login(email, name, picture)
    
    # Create JWT
    token = create_jwt(web_user)
    
    # Set cookie and redirect to dashboard
    response = RedirectResponse(url="/app/dashboard", status_code=302)
    response.set_cookie(
        key=JWT_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=JWT_EXPIRY_HOURS * 3600,
        path="/",
    )
    
    logger.info(f"Login successful: {email}")
    return response


@router.get("/logout")
async def logout():
    """Clear session cookie and redirect to login"""
    response = RedirectResponse(url="/app/login", status_code=302)
    response.delete_cookie(JWT_COOKIE_NAME, path="/")
    return response


@router.get("/me")
async def auth_me(user: dict = Depends(require_auth)):
    """Get current authenticated user info"""
    return {
        "email": user["sub"],
        "name": user["name"],
        "role": user["role"],
    }


# ========== AUTH MIDDLEWARE ==========

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect /app/* and /api/finance/* routes.
    Public routes: /auth/*, /api/health, /api/*, /health, /
    """
    
    PROTECTED_PREFIXES = ["/app/", "/api/finance/"]
    PUBLIC_PATHS = ["/app/login", "/app/login/"]
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Check if path needs protection
        needs_auth = any(path.startswith(p) for p in self.PROTECTED_PREFIXES)
        is_public = path in self.PUBLIC_PATHS
        
        if needs_auth and not is_public:
            user = get_current_user(request)
            if not user:
                # API routes get 401, web routes get redirected
                if path.startswith("/api/"):
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Not authenticated"}
                    )
                return RedirectResponse(url="/app/login")
            
            # Attach user to request state
            request.state.user = user
        
        response = await call_next(request)
        return response
