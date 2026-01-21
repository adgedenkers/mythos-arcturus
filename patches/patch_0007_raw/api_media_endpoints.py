"""
Mythos API - Media Endpoints
Sprint 1: Photo upload, storage, and retrieval

Add these endpoints to api/main.py
"""

from fastapi import BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import json
from pathlib import Path

# Request/Response Models for Media

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

# Media Upload Endpoint

@app.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media(
    request: MediaUploadRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Store media file metadata in database
    
    Flow:
    1. Receive metadata from Telegram bot (file already on disk)
    2. Get user info
    3. Insert media_files record
    4. If caption exists, create chat_message and link
    5. Queue background analysis
    6. Return media_id
    """
    
    # Get user
    user = get_user_by_identifier(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate aspect ratio
    aspect_ratio = request.width / request.height if request.height > 0 else 1.0
    
    # Determine media type
    media_type = 'photo'  # Could be extended for video/audio later
    
    try:
        # Insert media file record
        cursor.execute("""
            INSERT INTO media_files (
                user_uuid, conversation_id, filename, file_path,
                file_size_bytes, mime_type, media_type,
                telegram_file_id, telegram_file_unique_id,
                width, height, aspect_ratio
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user['uuid'], 
            request.conversation_id, 
            request.filename,
            request.file_path, 
            request.file_size, 
            request.mime_type, 
            media_type,
            request.telegram_file_id, 
            request.telegram_file_unique_id,
            request.width, 
            request.height, 
            aspect_ratio
        ))
        
        media_id = cursor.fetchone()[0]
        media_id_str = str(media_id)
        
        # If there's a caption, store it as a chat message
        message_id = None
        if request.caption and request.conversation_id:
            cursor.execute("""
                INSERT INTO chat_messages (
                    user_uuid, conversation_id, role, content, mode
                ) VALUES (%s, %s, 'user', %s, 'photo_caption')
                RETURNING message_id
            """, (
                user['uuid'], 
                request.conversation_id, 
                f"[Photo: {media_id_str[:8]}...] {request.caption}"
            ))
            
            message_id = cursor.fetchone()[0]
            
            # Link media to message
            cursor.execute("""
                UPDATE media_files SET message_id = %s WHERE id = %s
            """, (message_id, media_id))
        
        conn.commit()
        
        # Log success
        print(f"✅ Media stored: {media_id_str[:8]}... by {user['soul_display_name']}")
        
        # Queue background analysis (Phase 3 - not implemented yet)
        # background_tasks.add_task(analyze_photo_background, media_id_str, request.file_path)
        queued_for_analysis = False  # Will be True in Phase 3
        
        conn.close()
        
        return MediaUploadResponse(
            media_id=media_id_str,
            status="stored",
            queued_for_analysis=queued_for_analysis,
            file_path=request.file_path
        )
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"❌ Media upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Recent Photos Endpoint

@app.get("/media/recent", response_model=RecentPhotosResponse)
async def get_recent_photos(
    user_id: str,
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    """
    Get recent photos for a user
    
    Returns list of photos with metadata and processing status
    """
    
    # Get user
    user = get_user_by_identifier(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                id,
                filename,
                uploaded_at,
                width,
                height,
                processed,
                auto_tags,
                user_tags,
                analysis_data,
                conversation_id
            FROM media_files
            WHERE user_uuid = %s
              AND media_type = 'photo'
            ORDER BY uploaded_at DESC
            LIMIT %s
        """, (user['uuid'], limit))
        
        results = cursor.fetchall()
        conn.close()
        
        photos = []
        for row in results:
            photo_id, filename, uploaded_at, width, height, processed, auto_tags, user_tags, analysis_data, conv_id = row
            
            # Extract description from analysis_data if available
            description = None
            if analysis_data and isinstance(analysis_data, dict):
                if 'general' in analysis_data:
                    description = analysis_data['general']
                elif 'general_description' in analysis_data:
                    description = analysis_data['general_description']
            
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
        
        return RecentPhotosResponse(
            photos=photos,
            count=len(photos)
        )
        
    except Exception as e:
        conn.close()
        print(f"❌ Error fetching recent photos: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Photo by ID Endpoint

@app.get("/media/{media_id}")
async def get_media_by_id(
    media_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get detailed information about a specific media file
    
    Returns full metadata including analysis results
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                m.id,
                m.filename,
                m.file_path,
                m.uploaded_at,
                m.width,
                m.height,
                m.file_size_bytes,
                m.processed,
                m.processed_at,
                m.analysis_data,
                m.extracted_text,
                m.auto_tags,
                m.user_tags,
                m.conversation_id,
                u.soul_display_name,
                u.username
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
        
        # Check if file exists
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
        print(f"❌ Error fetching media: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Search Photos Endpoint

@app.get("/media/search/tag/{tag}")
async def search_photos_by_tag(
    tag: str,
    user_id: Optional[str] = None,
    limit: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """
    Search photos by tag
    
    Searches both auto_tags and user_tags
    Optionally filter by user_id
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build query based on whether user_id is provided
        if user_id:
            user = get_user_by_identifier(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            cursor.execute("""
                SELECT 
                    m.id,
                    m.filename,
                    m.uploaded_at,
                    m.width,
                    m.height,
                    m.auto_tags,
                    m.user_tags,
                    m.conversation_id,
                    u.soul_display_name
                FROM media_files m
                JOIN users u ON m.user_uuid = u.user_uuid
                WHERE m.user_uuid = %s
                  AND m.media_type = 'photo'
                  AND (%s = ANY(m.auto_tags) OR %s = ANY(m.user_tags))
                ORDER BY m.uploaded_at DESC
                LIMIT %s
            """, (user['uuid'], tag, tag, limit))
        else:
            cursor.execute("""
                SELECT 
                    m.id,
                    m.filename,
                    m.uploaded_at,
                    m.width,
                    m.height,
                    m.auto_tags,
                    m.user_tags,
                    m.conversation_id,
                    u.soul_display_name
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
                "tags": {
                    "auto": auto_tags or [],
                    "user": user_tags or []
                },
                "conversation_id": conv_id,
                "uploaded_by": soul_name
            })
        
        return {
            "tag": tag,
            "photos": photos,
            "count": len(photos)
        }
        
    except Exception as e:
        conn.close()
        print(f"❌ Error searching photos: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Add User Tag Endpoint

class AddTagRequest(BaseModel):
    media_id: str
    tag: str

@app.post("/media/tag/add")
async def add_user_tag(
    request: AddTagRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Add a user tag to a photo
    
    Tags are stored in user_tags array for provenance
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Add tag to user_tags array
        cursor.execute("""
            UPDATE media_files
            SET user_tags = array_append(
                COALESCE(user_tags, ARRAY[]::TEXT[]), 
                %s
            )
            WHERE id = %s
              AND NOT (%s = ANY(COALESCE(user_tags, ARRAY[]::TEXT[])))
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
        print(f"❌ Error adding tag: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Helper function to enhance conversation context with recent media
# Add this to the existing get_recent_conversation function

def get_recent_conversation_with_media(user_uuid, conversation_id, limit=5):
    """
    Enhanced version: Get last N messages AND recent photos for immediate context
    
    This gives the LLM awareness of visual context in the conversation
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get recent messages
        cursor.execute("""
            SELECT 
                m.role, 
                m.content, 
                m.created_at,
                mf.id as media_id,
                mf.filename,
                mf.width,
                mf.height,
                mf.processed,
                mf.analysis_data
            FROM chat_messages m
            LEFT JOIN media_files mf ON m.message_id = mf.message_id
            WHERE m.user_uuid = %s 
              AND m.conversation_id = %s
              AND m.created_at > NOW() - INTERVAL '10 minutes'
            ORDER BY m.created_at DESC
            LIMIT %s
        """, (user_uuid, conversation_id, limit))
        
        messages = cursor.fetchall()
        
        # Also get any photos uploaded in last minute that might not have messages yet
        cursor.execute("""
            SELECT 
                id,
                filename,
                width,
                height,
                uploaded_at,
                processed,
                analysis_data
            FROM media_files
            WHERE user_uuid = %s
              AND conversation_id = %s
              AND uploaded_at > NOW() - INTERVAL '1 minute'
              AND message_id IS NULL
            ORDER BY uploaded_at DESC
        """, (user_uuid, conversation_id))
        
        orphan_photos = cursor.fetchall()
        
        conn.close()
        
        if not messages and not orphan_photos:
            return None
        
        messages.reverse()  # Chronological order
        
        context_lines = []
        
        # Add message context
        for role, content, created_at, media_id, filename, width, height, processed, analysis_data in messages:
            if media_id:
                # Include photo metadata in context
                photo_info = f"{filename} ({width}x{height})"
                if processed and analysis_data:
                    # Add brief analysis summary if available
                    if isinstance(analysis_data, dict) and 'general' in analysis_data:
                        desc = analysis_data['general'][:150] + "..." if len(analysis_data['general']) > 150 else analysis_data['general']
                        photo_info += f" - {desc}"
                
                context_lines.append(f"{role}: [Photo: {photo_info}]")
                if content and not content.startswith('[Photo:'):
                    context_lines.append(f"Caption: {content[:200]}")
            else:
                content_short = content[:200] + "..." if len(content) > 200 else content
                context_lines.append(f"{role}: {content_short}")
        
        # Add orphan photos (just uploaded, no message yet)
        for photo_id, filename, width, height, uploaded_at, processed, analysis_data in orphan_photos:
            photo_info = f"{filename} ({width}x{height})"
            context_lines.append(f"[Just uploaded: {photo_info}]")
        
        return "\n".join(context_lines)
        
    except Exception as e:
        print(f"Error getting conversation with media: {e}")
        conn.close()
        return None


# Integration notes for existing /message endpoint:
# 
# In the handle_message function, replace the call to get_recent_conversation()
# with get_recent_conversation_with_media() to enable photo-aware conversations.
# 
# Example:
#   context = get_recent_conversation_with_media(user['uuid'], request.conversation_id)
#
# This gives the LLM awareness of recent photos in the conversation thread.
