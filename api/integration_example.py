#!/usr/bin/env python3
"""
Integration Example for Mythos API

This file shows how to integrate the orchestrator and context manager
with your existing main.py API.

DO NOT RUN THIS FILE DIRECTLY - it's a reference for manual integration.
"""

# =============================================================================
# STEP 1: Add imports at the top of main.py
# =============================================================================

"""
# Add these imports:
from fastapi import BackgroundTasks
from api.orchestrator import get_orchestrator, Orchestrator
from api.context_manager import ContextManager
"""

# =============================================================================
# STEP 2: Initialize after app creation (around line 45-50 in main.py)
# =============================================================================

"""
# Initialize orchestrator for async task dispatch
orchestrator: Orchestrator = None
try:
    orchestrator = get_orchestrator()
    print("✅ Orchestrator initialized")
except Exception as e:
    print(f"⚠️  Orchestrator not available: {e}")

# Initialize context manager
# Note: You may need to initialize Qdrant client here too
qdrant_client = None
try:
    from qdrant_client import QdrantClient
    qdrant_client = QdrantClient(host="localhost", port=6333)
    print("✅ Qdrant client initialized")
except Exception as e:
    print(f"⚠️  Qdrant not available: {e}")

context_manager = ContextManager(
    db_connection_func=get_db_connection,
    neo4j_driver=neo4j_driver,
    qdrant_client=qdrant_client
)
print("✅ Context manager initialized")
"""

# =============================================================================
# STEP 3: Modify your /message endpoint
# =============================================================================

"""
@app.post("/message")
async def handle_message(
    request: MessageRequest,
    background_tasks: BackgroundTasks,  # Add this parameter
    api_key: str = Depends(verify_api_key)
):
    # ... existing user lookup code ...
    
    # Store user message in database
    message_id = store_message(
        user_uuid=user['uuid'],
        conversation_id=request.conversation_id,
        role="user",
        content=request.message
    )
    
    # Get message count for this conversation
    message_count = get_message_count(request.conversation_id)
    
    # Assemble full context
    context = context_manager.assemble_context(
        conversation_id=request.conversation_id,
        user_uuid=user['uuid'],
        current_message=request.message,
        mode=request.mode
    )
    
    # Format context for LLM
    full_prompt = context_manager.format_context_for_llm(context)
    
    # Generate LLM response with full context
    response = generate_llm_response(full_prompt, model=request.model_preference)
    
    # Store assistant response
    store_message(
        user_uuid=user['uuid'],
        conversation_id=request.conversation_id,
        role="assistant",
        content=response
    )
    
    # Dispatch async extraction tasks (non-blocking)
    if orchestrator:
        # Dispatch all extraction tasks for this message
        background_tasks.add_task(
            orchestrator.dispatch_message_extraction,
            message_id=message_id,
            content=request.message,
            user_uuid=user['uuid'],
            conversation_id=request.conversation_id
        )
        
        # Check if summaries need pre-emptive rebuilding
        summary_tasks = orchestrator.check_summary_triggers(
            request.conversation_id,
            context['message_count']
        )
        
        for task in summary_tasks:
            background_tasks.add_task(
                orchestrator.dispatch_summary_rebuild,
                conversation_id=request.conversation_id,
                user_uuid=user['uuid'],
                tier=task['tier'],
                start_idx=task['start_idx'],
                end_idx=task['end_idx']
            )
    
    return MessageResponse(
        response=response,
        mode=request.mode,
        user=user.get('soul_display_name')
    )
"""

# =============================================================================
# STEP 4: Add orchestrator stats endpoint (optional but useful)
# =============================================================================

"""
@app.get("/orchestrator/stats")
async def get_orchestrator_stats(api_key: str = Depends(verify_api_key)):
    """Get orchestrator and worker statistics"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    return orchestrator.get_stats()
"""

# =============================================================================
# STEP 5: Add endpoint to manually trigger summary rebuild (optional)
# =============================================================================

"""
@app.post("/conversation/{conversation_id}/rebuild-summaries")
async def rebuild_conversation_summaries(
    conversation_id: str,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Manually trigger summary rebuild for a conversation"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    
    # Get user from conversation
    user_uuid = get_user_uuid_from_conversation(conversation_id)
    
    # Rebuild Tier 1
    tier1_id = orchestrator.dispatch_summary_rebuild(
        conversation_id=conversation_id,
        user_uuid=user_uuid,
        tier=1,
        start_idx=1,
        end_idx=20
    )
    
    # Rebuild Tier 2
    tier2_id = orchestrator.dispatch_summary_rebuild(
        conversation_id=conversation_id,
        user_uuid=user_uuid,
        tier=2,
        start_idx=21,
        end_idx=60
    )
    
    return {
        "status": "dispatched",
        "tier1_assignment": tier1_id,
        "tier2_assignment": tier2_id
    }
"""

# =============================================================================
# HELPER FUNCTIONS (add these if you don't have them)
# =============================================================================

"""
def get_message_count(conversation_id: str) -> int:
    """Get total message count for a conversation"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT COUNT(*) FROM chat_messages WHERE conversation_id = %s",
            (conversation_id,)
        )
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()


def get_user_uuid_from_conversation(conversation_id: str) -> str:
    """Get user UUID from a conversation"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT user_uuid FROM chat_messages WHERE conversation_id = %s LIMIT 1",
            (conversation_id,)
        )
        result = cur.fetchone()
        return str(result[0]) if result else None
    finally:
        cur.close()
        conn.close()
"""

print("This file is a reference - do not run directly.")
print("Copy the relevant sections into your main.py")
