#!/bin/bash
#
# Mythos API Media Endpoints Patcher
# Sprint 1: Add photo upload and retrieval to existing api/main.py
#
# This script:
# 1. Backs up the existing main.py
# 2. Adds required imports (if not present)
# 3. Adds media-related Pydantic models
# 4. Adds media endpoints before the final /user endpoint
# 5. Adds helper function for media-aware conversation context
# 6. Validates the result

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_FILE="/opt/mythos/api/main.py"
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${API_FILE}.backup.${BACKUP_TIMESTAMP}"

echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Mythos API Media Endpoints Patcher - Sprint 1${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: Running as root. Consider running as mythos user.${NC}"
    echo -e "   Press Ctrl+C to cancel, or Enter to continue..."
    read
fi

# Check if API file exists
if [ ! -f "$API_FILE" ]; then
    echo -e "${RED}❌ Error: $API_FILE not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found API file: $API_FILE"

# Create backup
echo -n "Creating backup... "
cp "$API_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✓${NC}"
echo -e "  Backup: $BACKUP_FILE"
echo ""

# Check if media endpoints already exist
if grep -q "def upload_media" "$API_FILE"; then
    echo -e "${YELLOW}⚠️  Media endpoints already exist in $API_FILE${NC}"
    echo -e "   This might be a re-run. Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Aborted. Backup preserved at: $BACKUP_FILE${NC}"
        exit 0
    fi
fi

# Step 1: Add imports if needed
echo -e "${BLUE}Step 1: Checking imports...${NC}"

if ! grep -q "from typing import Optional, List" "$API_FILE"; then
    echo -n "  Adding List to typing imports... "
    sed -i 's/from typing import Optional/from typing import Optional, List/' "$API_FILE"
    echo -e "${GREEN}✓${NC}"
else
    echo -e "  ${GREEN}✓${NC} List already imported"
fi

if ! grep -q "from pathlib import Path" "$API_FILE"; then
    echo -n "  Adding pathlib import... "
    sed -i '/^import json$/a from pathlib import Path' "$API_FILE"
    echo -e "${GREEN}✓${NC}"
else
    echo -e "  ${GREEN}✓${NC} pathlib already imported"
fi

echo ""

# Step 2: Add Pydantic models for media
echo -e "${BLUE}Step 2: Adding media Pydantic models...${NC}"

# Find where to insert models (after ConversationResponse model)
LINE_NUM=$(grep -n "class ConversationResponse" "$API_FILE" | tail -1 | cut -d: -f1)

if [ -z "$LINE_NUM" ]; then
    echo -e "${RED}❌ Could not find ConversationResponse model${NC}"
    echo -e "   Manual intervention required"
    exit 1
fi

# Find the end of that model (next blank line or next class)
END_LINE=$(tail -n +$((LINE_NUM + 1)) "$API_FILE" | grep -n -m 1 -E "^$|^class " | head -1 | cut -d: -f1)
INSERT_LINE=$((LINE_NUM + END_LINE))

echo -n "  Inserting media models at line $INSERT_LINE... "

# Create temp file with new models
cat > /tmp/media_models.txt << 'MODELS_EOF'

# Media Models (Sprint 1)
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

MODELS_EOF

# Insert the models
sed -i "${INSERT_LINE}r /tmp/media_models.txt" "$API_FILE"
rm /tmp/media_models.txt

echo -e "${GREEN}✓${NC}"
echo ""

# Step 3: Add helper function for media-aware conversation
echo -e "${BLUE}Step 3: Adding media-aware conversation helper...${NC}"

# Find get_recent_conversation function
FUNC_LINE=$(grep -n "^def get_recent_conversation" "$API_FILE" | cut -d: -f1)

if [ -z "$FUNC_LINE" ]; then
    echo -e "${YELLOW}⚠️  get_recent_conversation function not found${NC}"
    echo -e "   Skipping helper function insertion"
else
    echo -n "  Adding get_recent_conversation_with_media... "
    
    # Find end of get_recent_conversation function (next def or end of indentation)
    END_FUNC=$(tail -n +$((FUNC_LINE + 1)) "$API_FILE" | grep -n -m 1 "^def \|^# " | head -1 | cut -d: -f1)
    INSERT_FUNC=$((FUNC_LINE + END_FUNC))
    
    # Create the new function
    cat > /tmp/media_helper.txt << 'HELPER_EOF'

def get_recent_conversation_with_media(user_uuid, conversation_id, limit=5):
    """
    Enhanced version: Get last N messages AND recent photos for immediate context
    
    This gives the LLM awareness of visual context in the conversation
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get recent messages with media links
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

HELPER_EOF
    
    sed -i "${INSERT_FUNC}r /tmp/media_helper.txt" "$API_FILE"
    rm /tmp/media_helper.txt
    
    echo -e "${GREEN}✓${NC}"
fi

echo ""

# Step 4: Add media endpoints
echo -e "${BLUE}Step 4: Adding media endpoints...${NC}"

# Find the /user endpoint (should be near end of file)
USER_ENDPOINT=$(grep -n "^@app.get(\"/user" "$API_FILE" | cut -d: -f1)

if [ -z "$USER_ENDPOINT" ]; then
    echo -e "${RED}❌ Could not find /user endpoint${NC}"
    echo -e "   Manual intervention required"
    exit 1
fi

# Insert before /user endpoint
INSERT_ENDPOINTS=$((USER_ENDPOINT - 1))

echo -n "  Inserting media endpoints at line $INSERT_ENDPOINTS... "

# Create endpoints file
cat > /tmp/media_endpoints.txt << 'ENDPOINTS_EOF'

# ═══════════════════════════════════════════════════════════════════════════
# MEDIA ENDPOINTS (Sprint 1: Photo Upload & Retrieval)
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media(
    request: MediaUploadRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Store media file metadata in database
    File is already on disk, we're just registering it
    """
    user = get_user_by_identifier(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    aspect_ratio = request.width / request.height if request.height > 0 else 1.0
    media_type = 'photo'
    
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
            request.file_path, request.file_size, request.mime_type, media_type,
            request.telegram_file_id, request.telegram_file_unique_id,
            request.width, request.height, aspect_ratio
        ))
        
        media_id = cursor.fetchone()[0]
        media_id_str = str(media_id)
        
        # If caption exists, create chat_message and link
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
        
        # TODO: Queue background analysis (Sprint 3)
        queued_for_analysis = False
        
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
    """Search photos by tag (auto or user tags)"""
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

ENDPOINTS_EOF

sed -i "${INSERT_ENDPOINTS}r /tmp/media_endpoints.txt" "$API_FILE"
rm /tmp/media_endpoints.txt

echo -e "${GREEN}✓${NC}"
echo ""

# Step 5: Validate Python syntax
echo -e "${BLUE}Step 5: Validating Python syntax...${NC}"
echo -n "  Running syntax check... "

if python3 -m py_compile "$API_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo ""
    echo -e "${RED}❌ Syntax error detected!${NC}"
    echo -e "   Restoring backup..."
    cp "$BACKUP_FILE" "$API_FILE"
    echo -e "   ${GREEN}✓${NC} Restored original file"
    echo ""
    echo -e "   Check syntax manually with:"
    echo -e "   ${YELLOW}python3 -m py_compile $BACKUP_FILE${NC}"
    exit 1
fi

echo ""

# Step 6: Summary
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ API Patching Complete${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Changes made:${NC}"
echo "  • Added List to typing imports"
echo "  • Added pathlib.Path import"
echo "  • Added 5 media Pydantic models"
echo "  • Added get_recent_conversation_with_media() helper"
echo "  • Added 5 media endpoints:"
echo "    - POST /media/upload"
echo "    - GET  /media/recent"
echo "    - GET  /media/{media_id}"
echo "    - GET  /media/search/tag/{tag}"
echo "    - POST /media/tag/add"
echo ""
echo -e "${BLUE}Backup saved:${NC}"
echo "  $BACKUP_FILE"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Review changes: diff $BACKUP_FILE $API_FILE"
echo "  2. Restart API service: sudo systemctl restart mythos-api"
echo "  3. Check logs: sudo journalctl -u mythos-api -f"
echo "  4. Test endpoints: curl https://mythos-api.denkers.co/docs"
echo ""
echo -e "${YELLOW}Note:${NC} The database migration must be applied before testing."
echo ""
echo -e "${GREEN}Done!${NC}"

ENDPOINTS_EOF

# Make script executable
chmod +x /tmp/media_endpoints.txt 2>/dev/null || true
