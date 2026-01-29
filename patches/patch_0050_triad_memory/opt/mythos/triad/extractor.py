"""
Triad Memory System - Extraction Pipeline
Processes conversations through three extraction layers:
  - Grid (Knowledge)
  - Akashic (Wisdom)  
  - Prophetic (Vision)
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

import psycopg2
from psycopg2.extras import Json, execute_values

from .models import (
    Grid, GridContext, Entity, Action, State, Relationship, 
    Timestamp, Artifact, OpenThread, Declaration,
    Akashic, EnergyState, ArcType, Domain,
    Prophetic, Readiness, ReadinessLevel, Seed,
    TriadRecord
)

# Path to prompts
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """Load an extraction prompt from file."""
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text()


def hash_content(prompt: str, response: str) -> str:
    """Create SHA256 hash of conversation content."""
    content = f"{prompt}\n---\n{response}"
    return hashlib.sha256(content.encode()).hexdigest()


class TriadExtractor:
    """
    Extracts the three layers from a conversation.
    
    Requires an LLM backend for extraction. Configure via:
    - TRIAD_LLM_BACKEND: 'anthropic', 'openai', 'ollama', 'local'
    - Relevant API keys or endpoints
    """
    
    def __init__(
        self,
        db_connection_string: Optional[str] = None,
        llm_backend: Optional[str] = None,
        embedding_backend: Optional[str] = None
    ):
        self.db_conn_str = db_connection_string or os.getenv(
            "MYTHOS_DB_URL", 
            "postgresql://localhost/mythos"
        )
        self.llm_backend = llm_backend or os.getenv("TRIAD_LLM_BACKEND", "ollama")
        self.embedding_backend = embedding_backend or os.getenv("TRIAD_EMBEDDING_BACKEND", "ollama")
        
        # Load prompts
        self.grid_prompt = load_prompt("grid_extraction")
        self.akashic_prompt = load_prompt("akashic_extraction")
        self.prophetic_prompt = load_prompt("prophetic_extraction")
    
    def _get_db_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.db_conn_str)
    
    async def _call_llm(self, system_prompt: str, user_content: str) -> str:
        """
        Call the configured LLM backend.
        Override this method for your specific LLM setup.
        """
        if self.llm_backend == "ollama":
            return await self._call_ollama(system_prompt, user_content)
        elif self.llm_backend == "anthropic":
            return await self._call_anthropic(system_prompt, user_content)
        else:
            raise NotImplementedError(f"LLM backend not implemented: {self.llm_backend}")
    
    async def _call_ollama(self, system_prompt: str, user_content: str) -> str:
        """Call Ollama for extraction."""
        import httpx
        
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        model = os.getenv("TRIAD_OLLAMA_MODEL", "llama3.2")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "system": system_prompt,
                    "prompt": user_content,
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            return response.json()["response"]
    
    async def _call_anthropic(self, system_prompt: str, user_content: str) -> str:
        """Call Anthropic API for extraction."""
        import anthropic
        
        client = anthropic.AsyncAnthropic()
        response = await client.messages.create(
            model=os.getenv("TRIAD_ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}]
        )
        return response.content[0].text
    
    async def _get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for text."""
        if self.embedding_backend == "ollama":
            import httpx
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            model = os.getenv("TRIAD_EMBEDDING_MODEL", "nomic-embed-text")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{ollama_url}/api/embeddings",
                    json={"model": model, "prompt": text}
                )
                response.raise_for_status()
                return response.json()["embedding"]
        else:
            raise NotImplementedError(f"Embedding backend not implemented: {self.embedding_backend}")
    
    def _parse_grid_response(self, response: str) -> Grid:
        """Parse LLM response into Grid model."""
        data = json.loads(response)
        
        context = GridContext(
            setting=data.get("node_1_context", {}).get("setting"),
            prompt_intent=data.get("node_1_context", {}).get("prompt_intent"),
            initial_state=data.get("node_1_context", {}).get("initial_state")
        )
        
        entities = [Entity(**e) for e in data.get("node_2_entities", [])]
        actions = [Action(**a) for a in data.get("node_3_actions", [])]
        states = [State(**s) for s in data.get("node_4_states", [])]
        relationships = [
            Relationship(
                from_entity=r["from"], 
                to_entity=r["to"], 
                relationship=r["relationship"]
            ) for r in data.get("node_5_relationships", [])
        ]
        timestamps = [Timestamp(**t) for t in data.get("node_6_timestamps", [])]
        artifacts = [Artifact(**a) for a in data.get("node_7_artifacts", [])]
        open_threads = [OpenThread(**t) for t in data.get("node_8_open_threads", [])]
        declarations = [Declaration(**d) for d in data.get("node_9_declarations", [])]
        
        return Grid(
            context=context,
            entities=entities,
            actions=actions,
            states=states,
            relationships=relationships,
            timestamps=timestamps,
            artifacts=artifacts,
            open_threads=open_threads,
            declarations=declarations
        )
    
    def _parse_akashic_response(self, response: str) -> Akashic:
        """Parse LLM response into Akashic model."""
        data = json.loads(response)
        
        entry_state = EnergyState(
            valence=float(data["entry_state"]["valence"]),
            quality=data["entry_state"]["quality"]
        )
        exit_state = EnergyState(
            valence=float(data["exit_state"]["valence"]),
            quality=data["exit_state"]["quality"]
        )
        
        domains = [Domain(d) for d in data.get("domains", [])]
        
        return Akashic(
            entry_state=entry_state,
            exit_state=exit_state,
            arc_type=ArcType(data["arc_type"]),
            essence=data["essence"],
            pattern_signature=data["pattern_signature"],
            domains=domains,
            echoes=data.get("echoes"),
            witnessed_by=data.get("witnessed_by")
        )
    
    def _parse_prophetic_response(self, response: str) -> Prophetic:
        """Parse LLM response into Prophetic model."""
        data = json.loads(response)
        
        readiness = None
        if data.get("readiness"):
            readiness = Readiness(
                level=ReadinessLevel(data["readiness"]["level"]),
                what=data["readiness"]["what"]
            )
        
        seed = None
        if data.get("seed"):
            seed = Seed(
                name=data["seed"]["name"],
                description=data["seed"]["description"]
            )
        
        return Prophetic(
            vector=data["vector"],
            attractor=data["attractor"],
            invitation=data["invitation"],
            readiness=readiness,
            obstacle=data.get("obstacle"),
            seed=seed,
            convergences=data.get("convergences")
        )
    
    async def extract_grid(self, prompt: str, response: str) -> Grid:
        """Extract Grid (Knowledge) layer."""
        conversation = f"HUMAN:\n{prompt}\n\nASSISTANT:\n{response}"
        result = await self._call_llm(self.grid_prompt, conversation)
        grid = self._parse_grid_response(result)
        
        # Get embedding for the grid essence
        grid_summary = f"{grid.context.setting} {grid.context.prompt_intent}"
        grid.embedding = await self._get_embedding(grid_summary)
        
        return grid
    
    async def extract_akashic(self, prompt: str, response: str) -> Akashic:
        """Extract Akashic (Wisdom) layer."""
        conversation = f"HUMAN:\n{prompt}\n\nASSISTANT:\n{response}"
        result = await self._call_llm(self.akashic_prompt, conversation)
        akashic = self._parse_akashic_response(result)
        
        # Get embedding for the essence
        akashic.embedding = await self._get_embedding(akashic.essence)
        
        return akashic
    
    async def extract_prophetic(self, prompt: str, response: str) -> Prophetic:
        """Extract Prophetic (Vision) layer."""
        conversation = f"HUMAN:\n{prompt}\n\nASSISTANT:\n{response}"
        result = await self._call_llm(self.prophetic_prompt, conversation)
        prophetic = self._parse_prophetic_response(result)
        
        # Get embedding for trajectory
        trajectory_text = f"{prophetic.vector} {prophetic.attractor} {prophetic.invitation}"
        prophetic.embedding = await self._get_embedding(trajectory_text)
        
        return prophetic
    
    async def extract_all(
        self, 
        prompt: str, 
        response: str,
        spiral_day: Optional[int] = None,
        spiral_cycle: Optional[int] = None,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None
    ) -> TriadRecord:
        """
        Extract all three layers from a conversation.
        Returns a complete TriadRecord.
        """
        record = TriadRecord(
            spiral_day=spiral_day,
            spiral_cycle=spiral_cycle,
            source_type=source_type,
            source_id=source_id,
            content_hash=hash_content(prompt, response)
        )
        
        # Extract all three layers (could be parallelized)
        record.grid = await self.extract_grid(prompt, response)
        record.akashic = await self.extract_akashic(prompt, response)
        record.prophetic = await self.extract_prophetic(prompt, response)
        
        return record
    
    def save_record(self, record: TriadRecord) -> UUID:
        """Save a TriadRecord to PostgreSQL."""
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cur:
                # Insert main conversation record
                cur.execute("""
                    INSERT INTO triad_conversations 
                    (id, spiral_day, spiral_cycle, source_type, source_id, content_hash,
                     grid_extracted, akashic_extracted, prophetic_extracted)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    str(record.id),
                    record.spiral_day,
                    record.spiral_cycle,
                    record.source_type,
                    record.source_id,
                    record.content_hash,
                    record.grid is not None,
                    record.akashic is not None,
                    record.prophetic is not None
                ))
                conv_id = cur.fetchone()[0]
                
                # Insert Grid
                if record.grid:
                    g = record.grid
                    cur.execute("""
                        INSERT INTO triad_grid
                        (conversation_id, node_1_context, node_2_entities, node_3_actions,
                         node_4_states, node_5_relationships, node_6_timestamps,
                         node_7_artifacts, node_8_open_threads, node_9_declarations, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        conv_id,
                        Json({"setting": g.context.setting, "prompt_intent": g.context.prompt_intent, "initial_state": g.context.initial_state}),
                        Json([{"name": e.name, "type": e.type, "context": e.context} for e in g.entities]),
                        Json([{"action": a.action, "actor": a.actor, "completed": a.completed} for a in g.actions]),
                        Json([{"state": s.state, "who": s.who, "when": s.when} for s in g.states]),
                        Json([{"from": r.from_entity, "to": r.to_entity, "relationship": r.relationship} for r in g.relationships]),
                        Json([{"reference": t.reference, "type": t.type, "value": t.value} for t in g.timestamps]),
                        Json([{"name": a.name, "type": a.type, "action": a.action, "path": a.path} for a in g.artifacts]),
                        Json([{"thread": t.thread, "type": t.type, "priority": t.priority} for t in g.open_threads]),
                        Json([{"declaration": d.declaration, "speaker": d.speaker, "domain": d.domain} for d in g.declarations]),
                        g.embedding
                    ))
                
                # Insert Akashic
                if record.akashic:
                    a = record.akashic
                    cur.execute("""
                        INSERT INTO triad_akashic
                        (conversation_id, entry_valence, entry_quality, exit_valence, exit_quality,
                         arc_type, essence, pattern_signature, domains, echoes, witnessed_by, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        conv_id,
                        a.entry_state.valence,
                        a.entry_state.quality,
                        a.exit_state.valence,
                        a.exit_state.quality,
                        a.arc_type.value,
                        a.essence,
                        a.pattern_signature,
                        [d.value for d in a.domains],
                        a.echoes,
                        a.witnessed_by,
                        a.embedding
                    ))
                
                # Insert Prophetic
                if record.prophetic:
                    p = record.prophetic
                    cur.execute("""
                        INSERT INTO triad_prophetic
                        (conversation_id, vector, attractor, readiness, obstacle, 
                         invitation, seed, convergences, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        conv_id,
                        p.vector,
                        p.attractor,
                        Json({"level": p.readiness.level.value, "what": p.readiness.what}) if p.readiness else None,
                        p.obstacle,
                        p.invitation,
                        Json({"name": p.seed.name, "description": p.seed.description}) if p.seed else None,
                        p.convergences,
                        p.embedding
                    ))
                
                # Update pattern catalog
                if record.akashic:
                    cur.execute("""
                        INSERT INTO triad_patterns (signature, domain, occurrence_count)
                        VALUES (%s, %s, 1)
                        ON CONFLICT (signature) DO UPDATE
                        SET occurrence_count = triad_patterns.occurrence_count + 1
                    """, (
                        record.akashic.pattern_signature,
                        record.akashic.domains[0].value if record.akashic.domains else None
                    ))
                
                conn.commit()
                return record.id
                
        finally:
            conn.close()


# ======================
# CLI Interface
# ======================

async def main():
    """CLI for testing extraction."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Triad Memory Extractor")
    parser.add_argument("--prompt", "-p", help="Human prompt text or file path")
    parser.add_argument("--response", "-r", help="Assistant response text or file path")
    parser.add_argument("--layer", "-l", choices=["grid", "akashic", "prophetic", "all"], default="all")
    parser.add_argument("--save", "-s", action="store_true", help="Save to database")
    parser.add_argument("--spiral-day", type=int, help="Spiral day (1-9)")
    parser.add_argument("--spiral-cycle", type=int, help="Spiral cycle number")
    
    args = parser.parse_args()
    
    # Load from file if path provided
    prompt = args.prompt
    response = args.response
    
    if prompt and Path(prompt).exists():
        prompt = Path(prompt).read_text()
    if response and Path(response).exists():
        response = Path(response).read_text()
    
    if not prompt or not response:
        print("Please provide --prompt and --response")
        return
    
    extractor = TriadExtractor()
    
    if args.layer == "all":
        record = await extractor.extract_all(
            prompt, response,
            spiral_day=args.spiral_day,
            spiral_cycle=args.spiral_cycle
        )
        print(json.dumps({
            "grid": record.grid.__dict__ if record.grid else None,
            "akashic": record.akashic.__dict__ if record.akashic else None,
            "prophetic": record.prophetic.__dict__ if record.prophetic else None
        }, indent=2, default=str))
        
        if args.save:
            record_id = extractor.save_record(record)
            print(f"\nSaved as: {record_id}")
    else:
        method = getattr(extractor, f"extract_{args.layer}")
        result = await method(prompt, response)
        print(json.dumps(result.__dict__, indent=2, default=str))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
