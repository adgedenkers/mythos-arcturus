#!/usr/bin/env python3
"""
Conversation Engine — Shared Tool Schemas
===========================================
Pydantic models that appear as inputs/outputs across multiple tools.
These are the typed pipes that make tools chainable.

PersonData is the canonical example: person_lookup outputs it,
natal_chart accepts it, synastry accepts two of them, etc.

LOG-0018: Foundation deploy.
"""
from typing import Optional

from pydantic import Field

from .base import ToolInput, ToolOutput


# ─── Person ──────────────────────────────────────────────────────────────────

class PersonLookupInput(ToolInput):
    """Find a person by name and return their core data."""
    name: str = Field(description="Person's name or alias")


class PersonData(ToolOutput):
    """Core person record — output of person_lookup, input to many tools."""
    person_id: int = 0
    full_name: str = ""
    birth_date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD")
    birth_time: Optional[str] = Field(None, description="HH:MM 24h")
    birth_place: Optional[str] = Field(None, description="City, Country")
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None
    telegram_id: Optional[int] = None
    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


# ─── Astrology ───────────────────────────────────────────────────────────────

class NatalChartInput(ToolInput):
    """Calculate natal chart. Accepts mapped fields from PersonData or raw data."""
    name: str = Field(description="Person's name")
    birth_date: str = Field(description="ISO date YYYY-MM-DD")
    birth_time: str = Field(description="HH:MM 24h")
    birth_lat: float = Field(description="Birth latitude")
    birth_lon: float = Field(description="Birth longitude")


class PlanetPosition(ToolOutput):
    """Single planetary placement."""
    planet: str = ""
    sign: str = ""
    degree: float = 0.0
    house: int = 0
    retrograde: bool = False


class AspectData(ToolOutput):
    """Single aspect between two points."""
    planet_a: str = ""
    planet_b: str = ""
    aspect: str = ""       # conjunction, opposition, trine, etc.
    orb: float = 0.0
    applying: bool = False


class NatalChart(ToolOutput):
    """Complete natal chart — chainable into synastry, transits, etc."""
    name: str = ""
    birth_date: str = ""
    planets: list[PlanetPosition] = Field(default_factory=list)
    aspects: list[AspectData] = Field(default_factory=list)
    houses: dict[int, str] = Field(default_factory=dict)


class TransitOverlayInput(ToolInput):
    """Overlay current transits onto a natal chart."""
    natal_chart: NatalChart = Field(description="The natal chart to overlay on")
    transit_date: Optional[str] = Field(None, description="ISO date. None = today")


class TransitAspect(ToolOutput):
    """Transit planet aspecting natal point."""
    transit_planet: str = ""
    natal_planet: str = ""
    aspect: str = ""
    orb: float = 0.0
    applying: bool = False
    exact_date: Optional[str] = None


class TransitReport(ToolOutput):
    """Transit overlay result — chainable into interpretation."""
    name: str = ""
    transit_date: str = ""
    active_transits: list[TransitAspect] = Field(default_factory=list)
    pressure_score: float = Field(0.0, description="0-10 scale of transit intensity")


# ─── Finance ─────────────────────────────────────────────────────────────────

class FinanceSummaryInput(ToolInput):
    """Get financial summary for a time period."""
    period: str = Field(default="month", description="day, week, month, year")
    account: Optional[str] = Field(None, description="Filter by account name")


class FinanceSummary(ToolOutput):
    """Financial summary — chainable into projection."""
    period: str = ""
    total_income: float = 0.0
    total_expenses: float = 0.0
    net: float = 0.0
    top_categories: dict[str, float] = Field(default_factory=dict)
    account_balances: dict[str, float] = Field(default_factory=dict)


# ─── Diagnostics ─────────────────────────────────────────────────────────────

class SystemStatusInput(ToolInput):
    """Check system status."""
    component: Optional[str] = Field(None, description="Specific component to check")


class SystemStatus(ToolOutput):
    """System status report."""
    services: dict[str, str] = Field(default_factory=dict)  # name → status
    disk_usage_pct: float = 0.0
    memory_usage_pct: float = 0.0
    gpu_usage_pct: float = 0.0
    ollama_model_loaded: str = ""
    uptime_hours: float = 0.0
