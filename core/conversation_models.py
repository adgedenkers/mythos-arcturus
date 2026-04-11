"""
Mythos Conversation Metadata — Canonical Pydantic Model
========================================================
This is the single object that flows through the ingest pipeline:
  raw input → normalize into ConversationRecord → hash → upsert Postgres → sync Neo4j

Design principles:
  - One object, two stores. Postgres gets everything. Neo4j gets only IDs + relationships.
  - raw_payload holds the verbatim conversation log (Claude export, Ollama dump, paste, etc.)
  - turns[] is the structured/queryable version of the same data (indexed, not duplicated)
  - content_hash enables idempotent upsert and revision detection
  - spiritual_concepts are first-class, not lumped under generic entities
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


# ── Enums ────────────────────────────────────────────────────────────────────

class ConversationType(str, Enum):
    technical_build = "technical_build"
    channeling = "channeling"
    research = "research"
    life_log = "life_log"
    planning = "planning"
    genealogy = "genealogy"
    astrology = "astrology"
    mythos_dev = "mythos_dev"
    other = "other"


class InitiatorType(str, Enum):
    human = "human"
    model = "model"
    system = "system"
    unknown = "unknown"


class EdgeType(str, Enum):
    CONTINUES = "CONTINUES"
    BUILDS_ON = "BUILDS_ON"
    REFERENCES = "REFERENCES"
    CONTRADICTS = "CONTRADICTS"


# ── Sub-models ───────────────────────────────────────────────────────────────

class Participant(BaseModel):
    participant_type: Literal["human", "model", "system"]
    participant_id: str
    display_name: Optional[str] = None
    role: Optional[str] = None  # "user", "assistant", "observer", "channel"


class BranchPoint(BaseModel):
    turn_idx: int
    from_topic: Optional[str] = None
    to_topic: Optional[str] = None
    note: Optional[str] = None


class Decision(BaseModel):
    decision: str
    rationale: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    turn_idx: Optional[int] = None


class ActionItem(BaseModel):
    action: str
    owner: Optional[str] = None
    due: Optional[datetime] = None
    status: Optional[str] = None  # "pending", "done", "blocked", "deferred"
    turn_idx: Optional[int] = None


class SpiritualConceptRef(BaseModel):
    """First-class spiritual concept reference.

    Maps to (:SpiritualConcept) in Neo4j with its own label, not a generic entity.
    domain helps categorize: lineage, entity, practice, cosmology, order,
    incarnation, frequency, grid, etc.
    """
    concept_id: str  # stable slug: "arcturian-grid", "cathar-lineage", "thronescribe"
    name: str
    domain: Optional[str] = None


class EntityRefs(BaseModel):
    """Lightweight entity cache on the Postgres record.

    spiritual_concepts are ALSO stored as SpiritualConceptRef objects
    (with concept_id + domain) for the Neo4j sync. This field holds just
    the names for FTS indexing.
    """
    people: List[str] = Field(default_factory=list)
    systems: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    spiritual_concepts: List[str] = Field(default_factory=list)
    places: List[str] = Field(default_factory=list)
    other: List[str] = Field(default_factory=list)


class ConversationEdge(BaseModel):
    type: EdgeType
    to_conversation_id: UUID


class SpiralSignature(BaseModel):
    """Position across all nested cycles at a given moment.

    Computed from days_since_epoch using base-9 modular arithmetic.
    This is the 'calendar round' equivalent — the unique fingerprint
    of where someone sits across all cycle layers simultaneously.
    """
    pulse_day: int       # 1-9: which grid node is primary
    pulse_cycle: int     # which 9-day cycle you're in
    weave_day: int       # 1-81: which channel is active
    weave_cycle: int     # which 81-day cycle
    arc_day: int         # 1-729: position in ~2yr developmental arc
    arc_cycle: int       # which arc cycle
    long_day: int        # 1-6561: position in ~18yr life chapter
    long_cycle: int      # which long spiral cycle

    active_node: int     # = pulse_day (the grid node governing today)
    active_channel: Dict[str, int]  # {source_node, target_node} from weave_day
    arc_passage: int     # which of 9 passages within the arc (which node governs this passage)


class SpiralContext(BaseModel):
    """Spiral time context attached to a conversation record.

    Computed at ingest from the primary participant's active epoch.
    """
    epoch_id: Optional[UUID] = None
    epoch_started_at: Optional[str] = None   # date string: "2025-10-19"
    days_since_epoch: Optional[int] = None
    signature: Optional[SpiralSignature] = None


class SpiralEpoch(BaseModel):
    """A personal time anchor — one stratum in a person's spiral history.

    Epochs are sovereign. A person chooses when to start one, when to reset.
    Old epochs persist as historical strata. Only one is active (ended_at is None).
    """
    epoch_id: UUID = Field(default_factory=uuid4)
    person_id: str
    epoch_number: int = 1
    started_at: str          # date: "2025-10-19"
    ended_at: Optional[str] = None
    reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def compute_signature(self, target_date: str) -> SpiralSignature:
        """Compute the full spiral signature for a given date under this epoch."""
        from datetime import date as date_type
        epoch_date = date_type.fromisoformat(self.started_at)
        target = date_type.fromisoformat(target_date)
        days = (target - epoch_date).days

        if days < 0:
            raise ValueError(f"Target date {target_date} is before epoch {self.started_at}")

        pulse_day = (days % 9) + 1
        weave_day = (days % 81) + 1
        arc_day = (days % 729) + 1
        long_day = (days % 6561) + 1

        # Channel mapping: weave_day → (source_node, target_node) in 9×9 matrix
        source_node = ((weave_day - 1) // 9) + 1
        target_node = ((weave_day - 1) % 9) + 1

        # Arc passage: which of 9 macro-passages within the 729-day arc
        arc_passage = ((arc_day - 1) // 81) + 1

        return SpiralSignature(
            pulse_day=pulse_day,
            pulse_cycle=(days // 9) + 1,
            weave_day=weave_day,
            weave_cycle=(days // 81) + 1,
            arc_day=arc_day,
            arc_cycle=(days // 729) + 1,
            long_day=long_day,
            long_cycle=(days // 6561) + 1,
            active_node=pulse_day,
            active_channel={"source_node": source_node, "target_node": target_node},
            arc_passage=arc_passage,
        )


class Turn(BaseModel):
    turn_idx: int
    speaker_type: Literal["human", "model", "tool", "system"]
    speaker_id: Optional[str] = None
    created_at: Optional[datetime] = None
    token_estimate: Optional[int] = None
    content: Optional[str] = None
    content_json: Dict[str, Any] = Field(default_factory=dict)


# ── Main Record ──────────────────────────────────────────────────────────────

class ConversationRecord(BaseModel):
    """Canonical conversation metadata object.

    This is the single representation that flows through the pipeline.
    Postgres gets the full object serialized. Neo4j gets only:
      conversation_id, started_at, ended_at, type, source_model, revision
    plus relationship edges to Person, System, Topic, SpiritualConcept,
    ThreadGroup, and other Conversation nodes.
    """

    # ── Identity ─────────────────────────────────────────────────────────
    conversation_id: UUID = Field(default_factory=uuid4)
    source_model: str
    source_provider: Optional[str] = None
    session_id: Optional[str] = None
    thread_group_id: Optional[UUID] = None

    # ── Ingest ───────────────────────────────────────────────────────────
    ingest_source: Literal["api", "manual_paste", "import_file", "telegram"]
    ingest_idempotency_key: Optional[str] = None
    content_hash: Optional[str] = None
    revision: int = 1

    # ── Time ─────────────────────────────────────────────────────────────
    started_at: datetime
    ended_at: Optional[datetime] = None
    ingested_at: Optional[datetime] = None

    # ── Core ─────────────────────────────────────────────────────────────
    conversation_type: ConversationType = ConversationType.other
    initiated_by: InitiatorType = InitiatorType.unknown
    topic_tags: List[str] = Field(default_factory=list)
    participants: List[Participant] = Field(default_factory=list)

    # ── Structural ───────────────────────────────────────────────────────
    turn_count: int = 0
    token_estimate_total: Optional[int] = None
    token_estimates_per_turn: List[Dict[str, Any]] = Field(default_factory=list)

    produced_tools: bool = False
    produced_code: bool = False
    produced_files: bool = False
    produced_artifacts: bool = False

    branching_points: List[BranchPoint] = Field(default_factory=list)

    # ── Semantic ─────────────────────────────────────────────────────────
    summary: Optional[str] = None
    key_decisions: List[Decision] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)

    # ── Entities (Postgres cache for FTS) ────────────────────────────────
    entities: EntityRefs = Field(default_factory=EntityRefs)

    # ── Spiritual Concepts (first-class, for Neo4j sync) ─────────────────
    spiritual_concepts: List[SpiritualConceptRef] = Field(default_factory=list)

    # ── Graph Edges ──────────────────────────────────────────────────────
    edges: List[ConversationEdge] = Field(default_factory=list)

    # ── Spiral Time Context ──────────────────────────────────────────────
    # Computed at ingest from primary participant's active epoch.
    # Enables queries like "all Day 7 conversations" or "weave cycle 3 work"
    spiral_context: Optional[SpiralContext] = None

    # ── Raw Payload — the actual conversation log ────────────────────────
    # This is the verbatim export. Claude JSON, Ollama dump, pasted text.
    # Stored in Postgres only. Neo4j never sees this.
    raw_payload: Optional[Dict[str, Any]] = None

    # ── Turns — structured/indexed version of the conversation ───────────
    # Same data as raw_payload, different access pattern.
    # raw_payload = archive (never modified after ingest)
    # turns = queryable (indexed in conversation_turns table)
    turns: List[Turn] = Field(default_factory=list)

    # ── Overflow ─────────────────────────────────────────────────────────
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # ── Computed ─────────────────────────────────────────────────────────

    def compute_content_hash(self) -> str:
        """Compute SHA-256 hash from canonical fields for idempotent upsert.

        Excludes volatile fields (ingested_at, revision, content_hash itself)
        so that re-ingesting the same conversation produces the same hash.
        """
        canonical = self.model_dump(
            exclude={"ingested_at", "revision", "content_hash", "metadata"},
            mode="json",
        )
        raw = json.dumps(canonical, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    @model_validator(mode="after")
    def sync_turn_count(self) -> "ConversationRecord":
        """Keep turn_count in sync with actual turns if turns are provided."""
        if self.turns and self.turn_count == 0:
            self.turn_count = len(self.turns)
        return self

    @model_validator(mode="after")
    def sync_spiritual_concepts_to_entities(self) -> "ConversationRecord":
        """Ensure entities.spiritual_concepts stays in sync with the
        first-class spiritual_concepts list (for FTS indexing in Postgres)."""
        if self.spiritual_concepts:
            names = [sc.name for sc in self.spiritual_concepts]
            self.entities.spiritual_concepts = list(set(names))
        return self


# ── Example usage ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # ── Demonstrate spiral time computation ──────────────────────────────
    epoch = SpiralEpoch(
        person_id="katuar-el",
        epoch_number=1,
        started_at="2025-10-19",
        reason="Initial spiral activation",
    )

    # Compute today's signature
    today = "2026-02-28"
    sig = epoch.compute_signature(today)
    print(f"Ka'tuar'el spiral signature for {today}:")
    print(f"  Pulse: Day {sig.pulse_day} (Node {sig.active_node}), Cycle {sig.pulse_cycle}")
    print(f"  Weave: Day {sig.weave_day}, Channel ({sig.active_channel['source_node']}→{sig.active_channel['target_node']}), Cycle {sig.weave_cycle}")
    print(f"  Arc:   Day {sig.arc_day}, Passage {sig.arc_passage}, Cycle {sig.arc_cycle}")
    print(f"  Long:  Day {sig.long_day}, Cycle {sig.long_cycle}")
    print()

    # ── Build a conversation record with spiral context ──────────────────
    record = ConversationRecord(
        source_model="claude-opus-4-5",
        source_provider="anthropic",
        session_id="abc-123",
        ingest_source="api",
        started_at=datetime(2026, 2, 28, 14, 0, 0),
        conversation_type=ConversationType.mythos_dev,
        initiated_by=InitiatorType.human,
        topic_tags=["conversation-metadata", "schema-design", "spiral-time"],
        participants=[
            Participant(
                participant_type="human",
                participant_id="katuar-el",
                display_name="Ka'tuar'el",
                role="user",
            ),
            Participant(
                participant_type="model",
                participant_id="claude-opus-4-5",
                display_name="Claude",
                role="assistant",
            ),
        ],
        summary="Designed dual-store conversation metadata schema with nested spiral time architecture.",
        spiritual_concepts=[
            SpiritualConceptRef(
                concept_id="arcturian-grid",
                name="Arcturian Grid",
                domain="grid",
            ),
            SpiritualConceptRef(
                concept_id="spiral-time",
                name="Spiral Time",
                domain="cosmology",
            ),
        ],
        spiral_context=SpiralContext(
            epoch_id=epoch.epoch_id,
            epoch_started_at=epoch.started_at,
            days_since_epoch=(datetime(2026, 2, 28).date() - datetime(2025, 10, 19).date()).days,
            signature=sig,
        ),
        turns=[
            Turn(turn_idx=0, speaker_type="human", speaker_id="katuar-el",
                 content="Give me a good prompt for the conversation meta schema..."),
            Turn(turn_idx=1, speaker_type="model", speaker_id="claude-opus-4-5",
                 content="Here's a prompt you can drop into another LLM session..."),
        ],
        raw_payload={"format": "claude_export", "messages": ["..."]},
    )

    record.content_hash = record.compute_content_hash()

    print(record.model_dump_json(indent=2))
