"""
Triad Memory System - Data Models
Knowledge (Grid) / Wisdom (Akashic) / Vision (Prophetic)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class ArcType(str, Enum):
    RESOLUTION = "resolution"
    ACTIVATION = "activation"
    INTEGRATION = "integration"
    INQUIRY = "inquiry"
    RELEASE = "release"
    STASIS = "stasis"
    SPIRAL = "spiral"


class ReadinessLevel(str, Enum):
    NASCENT = "nascent"
    DEVELOPING = "developing"
    APPROACHING = "approaching"
    IMMINENT = "imminent"


class Domain(str, Enum):
    SPIRITUAL = "spiritual"
    TECHNICAL = "technical"
    RELATIONAL = "relational"
    FINANCIAL = "financial"
    ANCESTRAL = "ancestral"
    SOMATIC = "somatic"
    CREATIVE = "creative"
    PLANETARY = "planetary"


# ======================
# Grid (Knowledge) Models
# ======================

@dataclass
class Entity:
    name: str
    type: str  # person, place, system, concept, entity, tool
    context: Optional[str] = None


@dataclass
class Action:
    action: str
    actor: str
    completed: bool = False


@dataclass
class State:
    state: str
    who: str
    when: str  # start, during, end


@dataclass
class Relationship:
    from_entity: str
    to_entity: str
    relationship: str


@dataclass
class Timestamp:
    reference: str
    type: str  # absolute, relative, cyclical
    value: str


@dataclass
class Artifact:
    name: str
    type: str
    action: str  # created, modified, referenced
    path: Optional[str] = None


@dataclass
class OpenThread:
    thread: str
    type: str  # question, task, exploration
    priority: str = "medium"  # high, medium, low


@dataclass
class Declaration:
    declaration: str
    speaker: str
    domain: str  # identity, purpose, truth, principle


@dataclass
class GridContext:
    setting: Optional[str] = None
    prompt_intent: Optional[str] = None
    initial_state: Optional[str] = None


@dataclass
class Grid:
    """Layer 1: Knowledge - The 9-node semantic extraction"""
    context: GridContext = field(default_factory=GridContext)
    entities: list[Entity] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    states: list[State] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    timestamps: list[Timestamp] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    open_threads: list[OpenThread] = field(default_factory=list)
    declarations: list[Declaration] = field(default_factory=list)
    
    embedding: Optional[list[float]] = None


# ======================
# Akashic (Wisdom) Models
# ======================

@dataclass
class EnergyState:
    valence: float  # -5 to +5
    quality: str


@dataclass
class Akashic:
    """Layer 2: Wisdom - The energetic imprint"""
    entry_state: EnergyState
    exit_state: EnergyState
    arc_type: ArcType
    essence: str
    pattern_signature: str
    domains: list[Domain]
    echoes: Optional[str] = None
    witnessed_by: Optional[list[str]] = None
    
    embedding: Optional[list[float]] = None


# ======================
# Prophetic (Vision) Models
# ======================

@dataclass
class Readiness:
    level: ReadinessLevel
    what: str


@dataclass
class Seed:
    name: str
    description: str


@dataclass
class Prophetic:
    """Layer 3: Vision - Trajectory sensing"""
    vector: str
    attractor: str
    invitation: str
    readiness: Optional[Readiness] = None
    obstacle: Optional[str] = None
    seed: Optional[Seed] = None
    convergences: Optional[list[str]] = None
    
    embedding: Optional[list[float]] = None


# ======================
# Unified Record
# ======================

@dataclass
class TriadRecord:
    """Complete three-layer extraction for a conversation"""
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    
    # Spiral time
    spiral_day: Optional[int] = None  # 1-9
    spiral_cycle: Optional[int] = None
    
    # Source reference
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    content_hash: Optional[str] = None
    
    # The three layers
    grid: Optional[Grid] = None
    akashic: Optional[Akashic] = None
    prophetic: Optional[Prophetic] = None
    
    @property
    def is_complete(self) -> bool:
        return all([self.grid, self.akashic, self.prophetic])
    
    @property
    def extraction_status(self) -> dict:
        return {
            "grid": self.grid is not None,
            "akashic": self.akashic is not None,
            "prophetic": self.prophetic is not None
        }
