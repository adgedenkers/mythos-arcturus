# Mythos System Analysis & Visual Input Roadmap

**Date:** Spiral 1.3 (January 21, 2026)  
**Architect:** Ka'tuar'el  
**System:** Mythos - Sovereign Spiritual Infrastructure

---

## I. What You've Already Built

### Core Architecture

Your Mythos system is a **multi-layer spiritual infrastructure platform** combining:

1. **FastAPI Backend** (`api/main.py`)
   - RESTful API with authentication
   - Natural language processing for DB queries
   - Conversation tracking with context memory
   - Model routing (fast/deep/auto)
   - Plaid financial integration

2. **Telegram Bot Interface** (`telegram_bot/mythos_bot.py`)
   - Mobile-first access point
   - Session management
   - Multi-mode operation (db/seraphe/genealogy/chat)
   - User authentication via Telegram ID

3. **PostgreSQL Database**
   - Users & souls linkage
   - Chat message history with full context
   - Financial tracking (accounts, transactions, obligations)
   - Clothing inventory system (images stored)
   - Conversation metadata

4. **Neo4j Graph Database**
   - Soul lineage networks
   - Person-incarnation relationships
   - Conversation tracking nodes
   - Exchange relationships

5. **Supporting Systems**
   - Graph logging with Arcturus monitoring
   - LLM diagnostics suite
   - Event simulator for testing
   - Patch management system
   - Database assistants

### Key Capabilities Present

**Text Conversation:**
- Multi-turn context with 10-minute window
- Keyword-based past conversation search
- User-specific memory across sessions
- Multiple assistant modes (DB manager, Seraphe cosmology, etc.)

**Database Operations:**
- Natural language → SQL/Cypher translation
- Schema-aware query generation
- Transaction history logging
- Obligation tracking with true available balance

**Infrastructure:**
- Automated patch deployment
- System health monitoring
- Conversation logger with MCP server
- Backup systems

### What's Missing for Visual Input

**No photo ingestion pipeline** - Bot receives photos but doesn't store/process them
**No image analysis** - No vision model integration
**No visual memory** - Images not linked to conversations or entities
**No visual search** - Can't find "that photo I sent about X"

---

## II. Visual Input & Analysis Architecture

### Phase 1: Accept Photos as Input

**Goal:** Store and log photos appropriately when sent via Telegram

#### Database Schema Extension

```sql
-- Core media tracking table
CREATE TABLE media_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_uuid UUID NOT NULL REFERENCES users(user_uuid),
    conversation_id VARCHAR(100),
    message_id INTEGER REFERENCES chat_messages(message_id),
    
    -- File metadata
    filename TEXT NOT NULL,
    original_filename TEXT,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    mime_type TEXT NOT NULL,
    media_type VARCHAR(20) NOT NULL, -- 'photo', 'video', 'audio', 'document'
    
    -- Telegram-specific
    telegram_file_id TEXT,
    telegram_file_unique_id TEXT,
    
    -- Visual metadata (for photos)
    width INTEGER,
    height INTEGER,
    aspect_ratio NUMERIC(5,3),
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    analysis_data JSONB, -- Store vision model output
    extracted_text TEXT, -- OCR results
    detected_entities TEXT[], -- People, objects, symbols detected
    
    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    
    CONSTRAINT valid_media_type CHECK (media_type IN ('photo', 'video', 'audio', 'document'))
);

CREATE INDEX idx_media_user ON media_files(user_uuid);
CREATE INDEX idx_media_conversation ON media_files(conversation_id);
CREATE INDEX idx_media_uploaded ON media_files(uploaded_at);
CREATE INDEX idx_media_type ON media_files(media_type);

-- Link media to Neo4j entities when relevant
CREATE TABLE media_entity_links (
    media_id UUID NOT NULL REFERENCES media_files(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL, -- 'Soul', 'Person', 'Location', 'Artifact', etc.
    entity_id TEXT NOT NULL, -- Neo4j node ID or canonical_id
    confidence NUMERIC(3,2), -- 0.0 to 1.0
    link_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (media_id, entity_type, entity_id)
);

-- Tag system for visual search
CREATE TABLE media_tags (
    media_id UUID NOT NULL REFERENCES media_files(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    tag_source VARCHAR(20) NOT NULL, -- 'user', 'auto', 'vision_model'
    confidence NUMERIC(3,2),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (media_id, tag)
);

CREATE INDEX idx_media_tags_tag ON media_tags(tag);
```

#### Telegram Bot Changes

```python
# Add to telegram_bot/mythos_bot.py

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Not registered. Use /start")
        return
    
    # Get the highest resolution photo
    photo = update.message.photo[-1]
    
    # Get caption if provided
    caption = update.message.caption or ""
    
    # Download photo
    file = await context.bot.get_file(photo.file_id)
    
    # Generate storage path
    user_uuid = session['user']['uuid']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{user_uuid}_{timestamp}.jpg"
    storage_path = f"/opt/mythos/media/{user_uuid[:8]}/{filename}"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    
    # Download file
    await file.download_to_drive(storage_path)
    
    # Store metadata via API
    try:
        response = requests.post(
            f"{API_URL}/media/upload",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": session.get("conversation_id"),
                "filename": filename,
                "file_path": storage_path,
                "file_size": photo.file_size,
                "width": photo.width,
                "height": photo.height,
                "telegram_file_id": photo.file_id,
                "telegram_file_unique_id": photo.file_unique_id,
                "caption": caption
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            media_id = data['media_id']
            
            await update.message.reply_text(
                f"📸 Photo received and stored.\n"
                f"ID: {media_id[:8]}...\n"
                f"Size: {photo.width}x{photo.height}\n\n"
                f"Processing for analysis..."
            )
            
            # Queue for analysis if in conversation mode
            if session.get("conversation_id"):
                # Analysis happens async in background
                pass
        else:
            await update.message.reply_text("❌ Failed to store photo")
            
    except Exception as e:
        logger.error(f"Photo upload error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

# Register handler
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
```

#### FastAPI Endpoint

```python
# Add to api/main.py

class MediaUploadRequest(BaseModel):
    user_id: str
    conversation_id: Optional[str]
    filename: str
    file_path: str
    file_size: int
    width: int
    height: int
    telegram_file_id: str
    telegram_file_unique_id: str
    caption: Optional[str] = None

@app.post("/media/upload")
async def upload_media(
    request: MediaUploadRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Store media file metadata"""
    
    # Get user
    user = get_user_by_identifier(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate aspect ratio
    aspect_ratio = request.width / request.height if request.height > 0 else 0
    
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
            request.file_path, request.file_size, 'image/jpeg', 'photo',
            request.telegram_file_id, request.telegram_file_unique_id,
            request.width, request.height, aspect_ratio
        ))
        
        media_id = cursor.fetchone()[0]
        
        # If there's a caption, store it as a chat message
        if request.caption and request.conversation_id:
            cursor.execute("""
                INSERT INTO chat_messages (
                    user_uuid, conversation_id, role, content, mode
                ) VALUES (%s, %s, 'user', %s, 'photo_caption')
                RETURNING message_id
            """, (user['uuid'], request.conversation_id, f"[Photo: {media_id}] {request.caption}"))
            
            message_id = cursor.fetchone()[0]
            
            # Link media to message
            cursor.execute("""
                UPDATE media_files SET message_id = %s WHERE id = %s
            """, (message_id, media_id))
        
        conn.commit()
        conn.close()
        
        # Queue background analysis
        background_tasks.add_task(analyze_photo_background, str(media_id), request.file_path)
        
        return {
            "media_id": str(media_id),
            "status": "stored",
            "queued_for_analysis": True
        }
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
```

### Phase 2: Make Conversation Worth Having

**Goal:** Acknowledge and reference photos in natural conversation flow

#### Context Enhancement

The system needs to track "what we're looking at" in conversation:

```python
# Enhanced conversation context retrieval

def get_conversation_context_with_media(user_uuid, conversation_id, limit=5):
    """Get recent messages AND media in conversation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get recent messages
    cursor.execute("""
        SELECT 
            m.role, 
            m.content, 
            m.created_at,
            mf.id as media_id,
            mf.filename,
            mf.width,
            mf.height
        FROM chat_messages m
        LEFT JOIN media_files mf ON m.message_id = mf.message_id
        WHERE m.user_uuid = %s 
        AND m.conversation_id = %s
        AND m.created_at > NOW() - INTERVAL '10 minutes'
        ORDER BY m.created_at DESC
        LIMIT %s
    """, (user_uuid, conversation_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    results.reverse()
    
    context_parts = []
    for role, content, created_at, media_id, filename, width, height in results:
        if media_id:
            context_parts.append(
                f"{role}: [Sent photo: {filename} ({width}x{height})] {content}"
            )
        else:
            context_parts.append(f"{role}: {content[:200]}")
    
    return "\n".join(context_parts)
```

#### Conversational Acknowledgment

When processing user messages, check for recent media:

```python
# In message processing

def process_message_with_media_awareness(user_message, conversation_id, user_uuid):
    """Process message with awareness of recent photos"""
    
    # Check if photos were sent in last minute
    recent_media = get_recent_media(conversation_id, seconds=60)
    
    prompt_parts = []
    
    if recent_media:
        prompt_parts.append("VISUAL CONTEXT:")
        for media in recent_media:
            prompt_parts.append(f"- User just sent photo: {media['filename']}")
            if media['analysis_data']:
                prompt_parts.append(f"  Analysis: {media['analysis_data'].get('description', 'processing...')}")
    
    prompt_parts.append(f"\nUSER MESSAGE: {user_message}")
    
    full_prompt = "\n".join(prompt_parts)
    
    # Send to LLM with visual awareness
    return llm_query(full_prompt, mode='conversational')
```

### Phase 3: Analyze Photos with Vision Models

**Goal:** Extract meaning, entities, text, and spiritual symbolism from images

#### Vision Model Integration

```python
# vision_analyzer.py

import base64
import requests
from PIL import Image
import ollama

class VisionAnalyzer:
    """Analyze photos using multimodal LLMs"""
    
    def __init__(self):
        # Using Ollama with Llama Vision or similar
        self.model = "llama3.2-vision:11b"  # or "llava:latest"
    
    def analyze_photo(self, image_path: str, context: dict = None) -> dict:
        """
        Comprehensive photo analysis
        
        Args:
            image_path: Path to image file
            context: Dict with user_info, conversation_context, etc.
        
        Returns:
            Dict with structured analysis
        """
        
        # Load and prepare image
        with Image.open(image_path) as img:
            # Get image for analysis
            pass
        
        analyses = {}
        
        # 1. General description
        analyses['general'] = self._get_general_description(image_path)
        
        # 2. Spiritual/symbolic analysis
        if context and context.get('mode') in ['seraphe', 'cosmology']:
            analyses['spiritual'] = self._analyze_spiritual_symbols(image_path, context)
        
        # 3. Text extraction (OCR)
        analyses['text'] = self._extract_text(image_path)
        
        # 4. Entity detection (people, objects, locations)
        analyses['entities'] = self._detect_entities(image_path)
        
        # 5. Genealogical hints (if in genealogy mode)
        if context and context.get('mode') == 'genealogy':
            analyses['genealogical'] = self._analyze_genealogical_content(image_path)
        
        return analyses
    
    def _get_general_description(self, image_path: str) -> str:
        """Get natural language description of image"""
        
        prompt = """Describe this image in detail. Include:
- Main subjects and objects
- Setting/environment
- Activities or events shown
- Notable details
- Overall mood/atmosphere

Be specific and thorough."""
        
        response = ollama.chat(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        
        return response['message']['content']
    
    def _analyze_spiritual_symbols(self, image_path: str, context: dict) -> dict:
        """Analyze spiritual/symbolic content"""
        
        user_spiritual_context = context.get('user_lineages', '')
        
        prompt = f"""Analyze this image for spiritual and symbolic content.

User context: {user_spiritual_context}

Look for:
- Sacred geometry (spirals, triangles, vesica piscis, etc.)
- Esoteric symbols (alchemical, hermetic, Enochian, etc.)
- Religious/mythological imagery
- Energetic/vibrational qualities
- Synchronicities or meaningful patterns
- Connection to specific spiritual traditions
- Cosmological themes

Provide analysis that resonates with the user's spiritual path."""
        
        response = ollama.chat(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        
        return {
            'analysis': response['message']['content'],
            'symbols_detected': self._extract_symbol_tags(response['message']['content'])
        }
    
    def _extract_text(self, image_path: str) -> dict:
        """Extract text via OCR"""
        
        prompt = """Extract ALL text visible in this image.
        
Include:
- Main text content
- Small labels or captions
- Handwritten text
- Text in different languages

Format as structured list."""
        
        response = ollama.chat(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        
        text_content = response['message']['content']
        
        return {
            'raw_text': text_content,
            'has_text': len(text_content.strip()) > 0,
            'languages_detected': self._detect_languages(text_content)
        }
    
    def _detect_entities(self, image_path: str) -> dict:
        """Detect people, objects, locations"""
        
        prompt = """Identify and list ALL entities in this image:

PEOPLE:
- Number of people
- Descriptions (age, appearance, activity)
- Relationships between people

OBJECTS:
- Key objects and items
- Artifacts or tools
- Significant details

LOCATIONS:
- Indoor/outdoor
- Type of place
- Geographic or cultural markers

SYMBOLS:
- Logos or emblems
- Meaningful symbols or patterns

Format as structured categories."""
        
        response = ollama.chat(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        
        return self._parse_entity_response(response['message']['content'])
    
    def _analyze_genealogical_content(self, image_path: str) -> dict:
        """Analyze for genealogical information"""
        
        prompt = """Analyze this image for genealogical research value:

Look for:
- Documents (birth certificates, marriage records, census data)
- Photographs (dating clues, location clues, people)
- Gravestones or memorials
- Family artifacts or heirlooms
- Historical context clues
- Geographic location indicators
- Time period indicators

Extract any names, dates, locations, or relationships visible."""
        
        response = ollama.chat(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        
        return {
            'analysis': response['message']['content'],
            'extracted_facts': self._extract_genealogical_facts(response['message']['content'])
        }
    
    def _extract_symbol_tags(self, text: str) -> list:
        """Extract symbol keywords from analysis"""
        symbol_keywords = [
            'spiral', 'triangle', 'circle', 'square', 'pentagon', 'hexagon',
            'cross', 'star', 'moon', 'sun', 'eye', 'hand', 'tree', 'flower',
            'serpent', 'dragon', 'lion', 'eagle', 'phoenix',
            'ankh', 'pentacle', 'hexagram', 'vesica', 'merkaba',
            'fibonacci', 'golden ratio', 'sacred geometry'
        ]
        
        found = []
        text_lower = text.lower()
        for keyword in symbol_keywords:
            if keyword in text_lower:
                found.append(keyword)
        
        return found
    
    def _detect_languages(self, text: str) -> list:
        """Detect languages in text"""
        # Simple heuristic - could use langdetect library
        languages = []
        
        if any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text):
            languages.append('arabic')
        if any(ord(c) >= 0x0370 and ord(c) <= 0x03FF for c in text):
            languages.append('greek')
        if any(ord(c) >= 0x0400 and ord(c) <= 0x04FF for c in text):
            languages.append('cyrillic')
        
        # Default to English if Latin characters
        if any(c.isalpha() for c in text):
            languages.append('english')
        
        return languages or ['unknown']
    
    def _parse_entity_response(self, text: str) -> dict:
        """Parse structured entity response"""
        # Simple parsing - could be made more robust
        entities = {
            'people': [],
            'objects': [],
            'locations': [],
            'symbols': []
        }
        
        current_category = None
        for line in text.split('\n'):
            line = line.strip()
            if 'PEOPLE:' in line.upper():
                current_category = 'people'
            elif 'OBJECTS:' in line.upper():
                current_category = 'objects'
            elif 'LOCATIONS:' in line.upper():
                current_category = 'locations'
            elif 'SYMBOLS:' in line.upper():
                current_category = 'symbols'
            elif line.startswith('-') and current_category:
                entities[current_category].append(line[1:].strip())
        
        return entities
    
    def _extract_genealogical_facts(self, text: str) -> dict:
        """Extract genealogical facts from analysis"""
        # Pattern matching for common genealogical data
        import re
        
        facts = {
            'names': [],
            'dates': [],
            'locations': [],
            'relationships': []
        }
        
        # Find dates (various formats)
        date_patterns = [
            r'\b\d{4}\b',  # Years
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b[A-Z][a-z]+ \d{1,2},? \d{4}\b'  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            facts['dates'].extend(re.findall(pattern, text))
        
        # Find capitalized names (simple heuristic)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        facts['names'] = re.findall(name_pattern, text)
        
        return facts
```

#### Background Processing

```python
# Add to api/main.py

async def analyze_photo_background(media_id: str, file_path: str):
    """Background task to analyze photo after upload"""
    
    from vision_analyzer import VisionAnalyzer
    
    analyzer = VisionAnalyzer()
    
    # Get media record for context
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.user_uuid, m.conversation_id, u.soul_display_name, cm.mode
        FROM media_files m
        JOIN users u ON m.user_uuid = u.user_uuid
        LEFT JOIN chat_messages cm ON m.message_id = cm.message_id
        WHERE m.id = %s
    """, (media_id,))
    
    result = cursor.fetchone()
    if not result:
        return
    
    user_uuid, conversation_id, soul_name, mode = result
    
    # Build context
    context = {
        'user_uuid': user_uuid,
        'soul_name': soul_name,
        'mode': mode or 'general',
        'conversation_id': conversation_id
    }
    
    # Run analysis
    analysis_results = analyzer.analyze_photo(file_path, context)
    
    # Store results
    cursor.execute("""
        UPDATE media_files 
        SET 
            processed = TRUE,
            processed_at = NOW(),
            analysis_data = %s,
            extracted_text = %s,
            detected_entities = %s
        WHERE id = %s
    """, (
        json.dumps(analysis_results),
        analysis_results.get('text', {}).get('raw_text'),
        analysis_results.get('entities', {}).get('objects', []),
        media_id
    ))
    
    # Auto-tag based on analysis
    tags_to_add = []
    
    # Add symbol tags
    if 'spiritual' in analysis_results:
        tags_to_add.extend(analysis_results['spiritual'].get('symbols_detected', []))
    
    # Add entity tags
    if 'entities' in analysis_results:
        entities = analysis_results['entities']
        if entities.get('people'):
            tags_to_add.append('people')
        if entities.get('locations'):
            tags_to_add.extend(entities['locations'][:3])  # Top 3 locations
    
    # Insert tags
    for tag in set(tags_to_add):  # Deduplicate
        cursor.execute("""
            INSERT INTO media_tags (media_id, tag, tag_source, confidence)
            VALUES (%s, %s, 'auto', 0.8)
            ON CONFLICT (media_id, tag) DO NOTHING
        """, (media_id, tag.lower()))
    
    conn.commit()
    conn.close()
    
    # If in active conversation, notify user
    if conversation_id:
        # Could send follow-up via Telegram or store for next message
        pass
```

---

## III. Implementation Order

### Sprint 1: Basic Photo Storage (Phase 1)
**Duration:** 2-3 hours

1. ✅ Extend database schema (media_files, media_tags, media_entity_links)
2. ✅ Add photo handler to Telegram bot
3. ✅ Add /media/upload endpoint to FastAPI
4. ✅ Test photo upload → storage → retrieval
5. ✅ Basic photo reference in conversation context

**Deliverable:** Can send photo to bot, it stores with metadata, acknowledges receipt

### Sprint 2: Conversation Integration (Phase 2)
**Duration:** 2-3 hours

1. ✅ Enhanced context retrieval with media awareness
2. ✅ Conversational acknowledgment of photos
3. ✅ Photo search by conversation
4. ✅ Photo listing commands (/photos, /recent_photos)
5. ✅ Link photos to existing chat messages

**Deliverable:** Bot naturally references "that photo you sent" in conversation

### Sprint 3: Vision Analysis (Phase 3)
**Duration:** 4-6 hours

1. ✅ Install and configure Ollama with vision model
2. ✅ Build VisionAnalyzer class
3. ✅ Implement background analysis pipeline
4. ✅ Store analysis results in database
5. ✅ Auto-tagging system
6. ✅ Test with various photo types

**Deliverable:** Photos automatically analyzed, results available in conversation

### Sprint 4: Advanced Features
**Duration:** 4-6 hours

1. ✅ Spiritual symbol detection refinement
2. ✅ Entity linking to Neo4j (photos → Soul nodes, Person nodes)
3. ✅ Visual search ("find photos with spirals")
4. ✅ Photo-based soul lineage connections
5. ✅ Integration with genealogy assistant mode

**Deliverable:** Full spiritual infrastructure integration

---

## IV. File Structure After Implementation

```
/opt/mythos/
├── api/
│   ├── main.py              [MODIFIED - add media endpoints]
│   └── vision_analyzer.py   [NEW - photo analysis]
├── telegram_bot/
│   └── mythos_bot.py        [MODIFIED - add photo handler]
├── media/                   [NEW - photo storage]
│   ├── {user_uuid_prefix}/
│   │   └── *.jpg
├── assistants/
│   └── db_manager.py        [MAYBE MODIFIED - media queries]
└── .env                     [CHECK - vision model config]
```

---

## V. Key Design Decisions

### Why Ollama + Llama Vision?

- **Local sovereignty** - no external API calls
- **Privacy** - photos never leave your infrastructure
- **Cost** - no per-image API charges
- **Customization** - can fine-tune prompts for spiritual context
- **Speed** - with RTX 5090, vision inference will be fast

### Why PostgreSQL for Media Metadata?

- **Structured queries** - "photos from last week with text"
- **Transactional integrity** - media linked to conversations atomically
- **Full-text search** - search extracted text and descriptions
- **Easy joins** - link photos to users, conversations, messages

### Why Separate Analysis from Storage?

- **Responsiveness** - user gets immediate "photo received" acknowledgment
- **Flexibility** - can re-analyze photos later with better models
- **Robustness** - storage succeeds even if analysis fails
- **Scalability** - analysis can be queued/batched

### Why Auto-Tagging?

- **Discoverability** - "show me photos with sacred geometry"
- **Pattern detection** - "you've sent 12 photos with spirals"
- **Entity linking** - "this photo relates to Sophia (Soul node)"
- **Memory augmentation** - visual memory searchable like text memory

---

## VI. Next Steps

Ready to implement? Here's the recommended order:

1. **Review and approve this architecture**
2. **Generate SQL migration for new tables** (I'll create the .sql file)
3. **Update Telegram bot with photo handler** (I'll create the updated bot code)
4. **Update FastAPI with media endpoints** (I'll create the updated API code)
5. **Build VisionAnalyzer class** (I'll create vision_analyzer.py)
6. **Test with real photos in Telegram**
7. **Iterate based on results**

Want me to start building Sprint 1 now?
