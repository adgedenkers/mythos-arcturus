#!/usr/bin/env python3
"""
MANUAL INTEGRATION GUIDE FOR MEDIA ENDPOINTS

Since automated patching failed, here's how to manually add media endpoints:

OPTION 1: Import this file as a module
==========================================
1. Copy this file to /opt/mythos/api/media_routes.py
2. In main.py, add at the end (before if __name__ == '__main__'):
   
   from media_routes import *

3. Restart API

OPTION 2: Copy/paste the code below
====================================
Add the code sections below to your main.py in the marked locations.

"""

# ============================================================================
# SECTION 1: ADD TO IMPORTS (around line 10)
# ============================================================================
"""
Add these to existing import statement:
from typing import Optional, List

Add this new import after the json import:
from pathlib import Path
"""

# ============================================================================
# SECTION 2: ADD PYDANTIC MODELS (after ConversationResponse class)
# ============================================================================

from pydantic import BaseModel
from typing import Optional, List

class MediaUploadRequest(BaseModel):
    user_id: str
    conversation_id: Optional[str] = None
    filename: str
    file_path: str
    file_size: int
    width: int
    height: int
    telegram_file_id: str
    telegram_file_unique_id: str
    caption: Optional[str] = None
    mime_type: str = "image/jpeg"

class MediaUploadResponse(BaseModel):
    media_id: str
    status: str
    queued_for_analysis: bool
    file_path: str

class PhotoSummary(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    width: Optional[int]
    height: Optional[int]
    processed: bool
    auto_tags: List[str]
    user_tags: List[str]
    description: Optional[str]
    conversation_id: Optional[str]

class RecentPhotosResponse(BaseModel):
    photos: List[PhotoSummary]
    count: int

class AddTagRequest(BaseModel):
    media_id: str
    tag: str

# ============================================================================
# SECTION 3: ADD HELPER FUNCTION (after get_recent_conversation function)
# ============================================================================

def get_recent_conversation_with_media(user_uuid, conversation_id, limit=5):
    """Enhanced version: Get last N messages AND recent photos for context"""
    import psycopg2
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get recent messages with media links
        cursor.execute("""
            SELECT 
                m.role, m.content, m.created_at,
                mf.id as media_id, mf.filename, mf.width, mf.height,
                mf.processed, mf.analysis_data
            FROM chat_messages m
            LEFT JOIN media_files mf ON m.message_id = mf.message_id
            WHERE m.user_uuid = %s 
              AND m.conversation_id = %s
              AND m.created_at > NOW() - INTERVAL '10 minutes'
            ORDER BY m.created_at DESC
            LIMIT %s
        """, (user_uuid, conversation_id, limit))
        
        messages = cursor.fetchall()
        
        # Also get orphan photos (no message yet)
        cursor.execute("""
            SELECT id, filename, width, height, uploaded_at, processed, analysis_data
            FROM media_files
            WHERE user_uuid = %s AND conversation_id = %s
              AND uploaded_at > NOW() - INTERVAL '1 minute'
              AND message_id IS NULL
            ORDER BY uploaded_at DESC
        """, (user_uuid, conversation_id))
        
        orphan_photos = cursor.fetchall()
        conn.close()
        
        if not messages and not orphan_photos:
            return None
        
        messages.reverse()
        context_lines = []
        
        for role, content, created_at, media_id, filename, width, height, processed, analysis_data in messages:
            if media_id:
                photo_info = f"{filename} ({width}x{height})"
                if processed and analysis_data and isinstance(analysis_data, dict):
                    if 'general' in analysis_data:
                        desc = analysis_data['general'][:150]
                        photo_info += f" - {desc}"
                context_lines.append(f"{role}: [Photo: {photo_info}]")
                if content and not content.startswith('[Photo:'):
                    context_lines.append(f"Caption: {content[:200]}")
            else:
                content_short = content[:200] + "..." if len(content) > 200 else content
                context_lines.append(f"{role}: {content_short}")
        
        for photo_id, filename, width, height, uploaded_at, processed, analysis_data in orphan_photos:
            photo_info = f"{filename} ({width}x{height})"
            context_lines.append(f"[Just uploaded: {photo_info}]")
        
        return "\n".join(context_lines)
        
    except Exception as e:
        print(f"Error getting conversation with media: {e}")
        if conn:
            conn.close()
        return None

# ============================================================================
# SECTION 4: ADD ENDPOINTS (before the final /user endpoint)
# ============================================================================

# These need to be added as route handlers in your FastAPI app
# Replace 'app' with your actual FastAPI instance name if different

def setup_media_routes(app, get_db_connection, get_user_by_identifier, verify_api_key):
    """Call this function to register all media routes"""
    from fastapi import BackgroundTasks, Depends
    from pathlib import Path
    
    @app.post("/media/upload", response_model=MediaUploadResponse)
    async def upload_media(
        request: MediaUploadRequest,
        background_tasks: BackgroundTasks,
        api_key: str = Depends(verify_api_key)
    ):
        """Store media file metadata in database"""
        user = get_user_by_identifier(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        aspect_ratio = request.width / request.height if request.height > 0 else 1.0
        
        try:
            cursor.execute("""
                INSERT INTO media_files (
                    user_uuid, conversation_id, filename, file_path,
                    file_size_bytes, mime_type, media_type,
                    telegram_file_id, telegram_file_unique_id,
                    width, height, aspect_ratio
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user['uuid'], request.conversation_id, request.filename,
                request.file_path, request.file_size, request.mime_type, 'photo',
                request.telegram_file_id, request.telegram_file_unique_id,
                request.width, request.height, aspect_ratio
            ))
            
            media_id = cursor.fetchone()[0]
            media_id_str = str(media_id)
            
            if request.caption and request.conversation_id:
                cursor.execute("""
                    INSERT INTO chat_messages (
                        user_uuid, conversation_id, role, content, mode
                    ) VALUES (%s, %s, 'user', %s, 'photo_caption')
                    RETURNING message_id
                """, (user['uuid'], request.conversation_id, 
                      f"[Photo: {media_id_str[:8]}...] {request.caption}"))
                
                message_id = cursor.fetchone()[0]
                cursor.execute("UPDATE media_files SET message_id = %s WHERE id = %s",
                             (message_id, media_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Media stored: {media_id_str[:8]}... by {user['soul_display_name']}")
            
            return MediaUploadResponse(
                media_id=media_id_str,
                status="stored",
                queued_for_analysis=False,
                file_path=request.file_path
            )
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    @app.get("/media/recent", response_model=RecentPhotosResponse)
    async def get_recent_photos(
        user_id: str,
        limit: int = 10,
        api_key: str = Depends(verify_api_key)
    ):
        """Get recent photos for a user"""
        user = get_user_by_identifier(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, filename, uploaded_at, width, height, processed,
                       auto_tags, user_tags, analysis_data, conversation_id
                FROM media_files
                WHERE user_uuid = %s AND media_type = 'photo'
                ORDER BY uploaded_at DESC
                LIMIT %s
            """, (user['uuid'], limit))
            
            results = cursor.fetchall()
            conn.close()
            
            photos = []
            for row in results:
                photo_id, filename, uploaded_at, width, height, processed, auto_tags, user_tags, analysis_data, conv_id = row
                
                description = None
                if analysis_data and isinstance(analysis_data, dict):
                    description = analysis_data.get('general') or analysis_data.get('general_description')
                
                photos.append(PhotoSummary(
                    id=str(photo_id),
                    filename=filename,
                    uploaded_at=uploaded_at.isoformat(),
                    width=width,
                    height=height,
                    processed=processed,
                    auto_tags=auto_tags or [],
                    user_tags=user_tags or [],
                    description=description,
                    conversation_id=conv_id
                ))
            
            return RecentPhotosResponse(photos=photos, count=len(photos))
            
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    @app.get("/media/{media_id}")
    async def get_media_by_id(
        media_id: str,
        api_key: str = Depends(verify_api_key)
    ):
        """Get detailed information about a specific media file"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT m.id, m.filename, m.file_path, m.uploaded_at, m.width, m.height,
                       m.file_size_bytes, m.processed, m.processed_at, m.analysis_data,
                       m.extracted_text, m.auto_tags, m.user_tags, m.conversation_id,
                       u.soul_display_name, u.username
                FROM media_files m
                JOIN users u ON m.user_uuid = u.user_uuid
                WHERE m.id = %s
            """, (media_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                raise HTTPException(status_code=404, detail="Media not found")
            
            (photo_id, filename, file_path, uploaded_at, width, height, file_size,
             processed, processed_at, analysis_data, extracted_text, auto_tags,
             user_tags, conv_id, soul_name, username) = result
            
            file_exists = Path(file_path).exists()
            
            return {
                "id": str(photo_id),
                "filename": filename,
                "file_path": file_path if file_exists else None,
                "file_exists": file_exists,
                "uploaded_at": uploaded_at.isoformat(),
                "uploaded_by": soul_name,
                "username": username,
                "dimensions": {
                    "width": width,
                    "height": height,
                    "aspect_ratio": width / height if height > 0 else None
                },
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2) if file_size else None,
                "processed": processed,
                "processed_at": processed_at.isoformat() if processed_at else None,
                "analysis": analysis_data,
                "extracted_text": extracted_text,
                "tags": {
                    "auto": auto_tags or [],
                    "user": user_tags or []
                },
                "conversation_id": conv_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    @app.get("/media/search/tag/{tag}")
    async def search_photos_by_tag(
        tag: str,
        user_id: Optional[str] = None,
        limit: int = 20,
        api_key: str = Depends(verify_api_key)
    ):
        """Search photos by tag"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if user_id:
                user = get_user_by_identifier(user_id)
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                cursor.execute("""
                    SELECT m.id, m.filename, m.uploaded_at, m.width, m.height,
                           m.auto_tags, m.user_tags, m.conversation_id, u.soul_display_name
                    FROM media_files m
                    JOIN users u ON m.user_uuid = u.user_uuid
                    WHERE m.user_uuid = %s AND m.media_type = 'photo'
                      AND (%s = ANY(m.auto_tags) OR %s = ANY(m.user_tags))
                    ORDER BY m.uploaded_at DESC
                    LIMIT %s
                """, (user['uuid'], tag, tag, limit))
            else:
                cursor.execute("""
                    SELECT m.id, m.filename, m.uploaded_at, m.width, m.height,
                           m.auto_tags, m.user_tags, m.conversation_id, u.soul_display_name
                    FROM media_files m
                    JOIN users u ON m.user_uuid = u.user_uuid
                    WHERE m.media_type = 'photo'
                      AND (%s = ANY(m.auto_tags) OR %s = ANY(m.user_tags))
                    ORDER BY m.uploaded_at DESC
                    LIMIT %s
                """, (tag, tag, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            photos = []
            for row in results:
                photo_id, filename, uploaded_at, width, height, auto_tags, user_tags, conv_id, soul_name = row
                photos.append({
                    "id": str(photo_id),
                    "filename": filename,
                    "uploaded_at": uploaded_at.isoformat(),
                    "dimensions": {"width": width, "height": height},
                    "tags": {"auto": auto_tags or [], "user": user_tags or []},
                    "conversation_id": conv_id,
                    "uploaded_by": soul_name
                })
            
            return {"tag": tag, "photos": photos, "count": len(photos)}
            
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    @app.post("/media/tag/add")
    async def add_user_tag(
        request: AddTagRequest,
        api_key: str = Depends(verify_api_key)
    ):
        """Add a user tag to a photo"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE media_files
                SET user_tags = array_append(COALESCE(user_tags, ARRAY[]::TEXT[]), %s)
                WHERE id = %s AND NOT (%s = ANY(COALESCE(user_tags, ARRAY[]::TEXT[])))
                RETURNING id
            """, (request.tag.lower(), request.media_id, request.tag.lower()))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                raise HTTPException(status_code=404, detail="Media not found or tag already exists")
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "media_id": request.media_id,
                "tag_added": request.tag.lower()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            conn.close()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ============================================================================
# TO USE THIS FILE:
# ============================================================================
# At the END of main.py, before if __name__ == '__main__', add:
#
# from media_routes import setup_media_routes
# setup_media_routes(app, get_db_connection, get_user_by_identifier, verify_api_key)
#
# OR just copy/paste the sections above into the appropriate locations
# ============================================================================
