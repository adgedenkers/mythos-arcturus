# CONVERSATION_ENGINE_SPEC.md
## Iris Conversation Engine — The Missing Layer

**Author:** Ka'tuar'el  
**Date:** 2026-03-17  
**Status:** DRAFT — Confirm before building  
**Stream:** LOG (conversation routing, LLM orchestration, tool chains)  
**Revision:** 2 — Pydantic-native, chainable tools, orchestration layer

---

## The Problem

Iris has one pipe: message → prompt assembly → Ollama → response. Every conversation goes through the same path regardless of intent. Skills are matched by keyword. Prompt assembly is monolithic. There's no way to change how the model thinks, what tools it has access to, how creative it is, or what shape the output takes — per message.

The Ollama/Qwen3 API exposes seven independent control levers per request. We use almost none of them. Skills aren't composable. Handlers duplicate plumbing. There's no event system, no chain execution, no self-observation.

---

## The Solution

A **Conversation Engine** built on Pydantic end-to-end. Every config, every tool input, every tool output, every chain link, every event — is a typed Pydantic model with validation, serialization, and automatic JSON schema generation.

Three layers:

1. **Call Layer** — Handles the mechanics of talking to Ollama
2. **Orchestration Layer** — Chains, events, multi-model routing, context budget
3. **Consciousness Layer** — Gravity, crystallization, night cycle, self-observation (spec'd separately)

This document covers layers 1 and 2.

---

## Design Principle: Pydantic Everywhere

Every boundary in the system is a Pydantic model. No raw dicts. No untyped JSON. No hoping the shape is right.

```python
from pydantic import BaseModel, Field
```

**Why this matters:**
- `model.model_json_schema()` generates the JSON schema Ollama needs for structured output — automatically
- `model.model_validate_json(response)` validates LLM output against the schema — automatically
- Tool inputs and outputs are type-checked at chain composition time — before execution
- Serialization to Postgres, Neo4j, Redis, or wire format is `.model_dump()` — one call
- IDE autocompletion, type checking, and refactoring work across the entire system

---

## Part 1: The Seven Levers

These are the control surfaces available in the Ollama API today. Every one is settable per request.

### 1. Thinking Mode (`thinking: bool`)

Qwen3 supports `/think` and `/no_think` as inline prompt switches. When on, the model reasons in `<think>...</think>` tags before responding. When off, direct answer, lower latency, fewer tokens.

- Quick lookups, commands, diagnostics → `/no_think`
- Complex questions, spiritual guidance, analysis → `/think`
- Two-pass pattern: first pass captures reasoning, second pass uses it for structured output

### 2. Structured Output (`format`)

Pass a JSON schema via `format` parameter. The model is grammar-constrained to return valid JSON matching that schema. Not a suggestion — enforcement. With Pydantic: `format=MyModel.model_json_schema()`.

### 3. Tool Calling (`tools`)

Pass function definitions in `tools` array. Model returns `tool_calls` when it decides a tool is needed. Execute the function, feed result back as `role: "tool"`. Qwen3 supports parallel tool calls.

### 4. System Prompt (`system`)

Overrides Modelfile system prompt per request. Composable from layers.

### 5. Temperature + Sampling (`options`)

`temperature`, `top_k`, `top_p`, `min_p`, `repeat_penalty`, `presence_penalty`, `frequency_penalty` — all per request.

### 6. Context Window (`num_ctx`)

Adjustable per request. Default 2048 is too low. Range: 2048–32768+ depending on mode.

### 7. Stop Sequences (`stop`)

Tokens that immediately halt generation. Used for two-pass thinking and constrained output.

---

## Part 2: Call Layer

### ConversationConfig

The single object that controls every aspect of a model call.

```python
from pydantic import BaseModel, Field
from typing import Optional, Any


class SamplingConfig(BaseModel):
    """LLM sampling parameters."""
    temperature: float = 0.7
    top_k: int = 40
    top_p: float = 0.9
    min_p: float = 0.0
    repeat_penalty: float = 1.1
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    seed: Optional[int] = None


class ConversationConfig(BaseModel):
    """Complete configuration for a single LLM call.
    
    Every field is typed. The engine assembles this per message.
    Nothing is guessed, nothing is implicit.
    """
    
    # Identity
    system_prompt: str = Field(
        description="Assembled from mode layers + context"
    )
    
    # Model
    model: str = Field(
        default="qwen3:30b-a3b",
        description="Ollama model tag"
    )
    
    # Thinking
    thinking: bool = Field(
        default=True,
        description="Enable /think (reasoning) or /no_think (direct)"
    )
    thinking_budget: Optional[int] = Field(
        default=None,
        description="Max thinking tokens. None = unlimited"
    )
    
    # Tools — Ollama-formatted tool definitions
    tools: Optional[list[dict]] = Field(
        default=None,
        description="Available tool definitions for this call"
    )
    
    # Output shape — JSON schema for structured output
    format: Optional[dict] = Field(
        default=None,
        description="Pydantic model_json_schema() for constrained output"
    )
    
    # Sampling
    sampling: SamplingConfig = Field(default_factory=SamplingConfig)
    
    # Context
    num_ctx: int = Field(
        default=8192,
        description="Context window size in tokens"
    )
    num_predict: int = Field(
        default=-1,
        description="Max response tokens. -1 = model decides"
    )
    
    # Control
    stop: Optional[list[str]] = Field(
        default=None,
        description="Stop sequences that halt generation"
    )
    
    # Metadata (not sent to Ollama — used by engine)
    mode: str = Field(
        default="conversation",
        description="Active conversation mode name"
    )
    requires_memory: bool = False
    requires_graph: bool = False
    
    def to_ollama_payload(self, messages: list[dict]) -> dict:
        """Build the exact payload for Ollama's /api/chat endpoint."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.sampling.temperature,
                "top_k": self.sampling.top_k,
                "top_p": self.sampling.top_p,
                "min_p": self.sampling.min_p,
                "repeat_penalty": self.sampling.repeat_penalty,
                "presence_penalty": self.sampling.presence_penalty,
                "frequency_penalty": self.sampling.frequency_penalty,
                "num_ctx": self.num_ctx,
                "num_predict": self.num_predict,
            },
        }
        if self.sampling.seed is not None:
            payload["options"]["seed"] = self.sampling.seed
        if self.tools:
            payload["tools"] = self.tools
        if self.format:
            payload["format"] = self.format
        if self.stop:
            payload["options"]["stop"] = self.stop
        return payload
```

### ConversationMode

A named preset loaded from YAML.

```python
class ConversationMode(BaseModel):
    """A named configuration preset for a type of conversation."""
    
    name: str
    description: str
    
    # Lever defaults
    thinking: bool = True
    temperature: float = 0.7
    num_ctx: int = 8192
    num_predict: int = -1
    
    # Tool access
    allowed_tools: Optional[list[str]] = Field(
        default=None,
        description="Tool names or categories. None or ['*'] = all"
    )
    
    # Output
    force_format: Optional[str] = Field(
        default=None,
        description="Pydantic model class name to force as output schema"
    )
    
    # Model override
    model: Optional[str] = None
    
    # System prompt layers to compose
    system_layers: list[str] = Field(
        default_factory=lambda: ["base"]
    )
```

### Built-in Modes

```yaml
# /opt/mythos/config/conversation_modes.yaml

default_model: "qwen3:30b-a3b"
deep_model: "qwen3:32b"

default_config:
  thinking: true
  temperature: 0.7
  num_ctx: 8192
  num_predict: -1

modes:
  command:
    description: "Quick commands, lookups, diagnostics"
    thinking: false
    temperature: 0.2
    num_ctx: 4096
    num_predict: 500
    allowed_tools: ["*"]
    system_layers: ["base"]
    
  conversation:
    description: "General back-and-forth"
    thinking: true
    temperature: 0.7
    num_ctx: 8192
    allowed_tools: ["*"]
    system_layers: ["base"]
    
  deep:
    description: "Complex analysis, multi-step reasoning"
    thinking: true
    temperature: 0.5
    num_ctx: 16384
    allowed_tools: ["*"]
    system_layers: ["base", "deep"]
    
  spiritual:
    description: "Channeling, guidance, field work"
    thinking: true
    temperature: 0.8
    num_ctx: 16384
    allowed_tools: ["astrology", "person_lookup", "soul_graph", "transit"]
    system_layers: ["base", "spiritual"]
    
  builder:
    description: "Technical work, code generation, system building"
    thinking: true
    temperature: 0.3
    num_ctx: 16384
    allowed_tools: ["diagnostics", "file_ops", "database"]
    system_layers: ["base", "builder"]
    
  night_cycle:
    description: "2AM integration — full context, deep processing"
    thinking: true
    temperature: 0.6
    num_ctx: 32768
    model: "qwen3:32b"
    allowed_tools: ["*"]
    system_layers: ["base", "night_cycle"]

  seraphe:
    description: "Seraphe-specific conversation mode"
    thinking: true
    temperature: 0.8
    num_ctx: 16384
    allowed_tools: ["astrology", "person_lookup", "soul_graph", "transit"]
    system_layers: ["base", "seraphe"]

user_routes:
  8069190169:
    default_mode: "seraphe"
  7811548479:
    default_mode: "conversation"
```

---

## Part 3: Chainable Tools — The Core Innovation

### The Principle

Every tool is a pure function with a typed Pydantic input and a typed Pydantic output. The output of one tool can be piped into the input of the next. The engine validates compatibility at composition time, before anything runs.

This is Unix philosophy applied to AI: small tools, typed pipes, composable chains.

### ToolInput / ToolOutput Base Classes

```python
class ToolInput(BaseModel):
    """Base class for all tool inputs. Every tool declares what it needs."""
    class Config:
        extra = "forbid"  # No surprise fields


class ToolOutput(BaseModel):
    """Base class for all tool outputs. Every tool declares what it produces."""
    success: bool = True
    error: Optional[str] = None
    
    class Config:
        extra = "forbid"
```

### Example: Astrology Tools as Typed, Chainable Units

```python
# ─── Person Lookup ───────────────────────────────────────────────

class PersonLookupInput(ToolInput):
    """Find a person by name and return their core data."""
    name: str = Field(description="Person's name or alias")


class PersonData(ToolOutput):
    """Core person record — output of person_lookup, input to many tools."""
    person_id: int
    full_name: str
    birth_date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD")
    birth_time: Optional[str] = Field(None, description="HH:MM 24h")
    birth_place: Optional[str] = Field(None, description="City, Country")
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None
    telegram_id: Optional[int] = None
    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


# ─── Natal Chart ─────────────────────────────────────────────────

class NatalChartInput(ToolInput):
    """Calculate natal chart. Accepts PersonData or raw birth data."""
    # Can be filled from PersonData output OR manually
    name: str
    birth_date: str = Field(description="ISO date YYYY-MM-DD")
    birth_time: str = Field(description="HH:MM 24h")
    birth_lat: float
    birth_lon: float


class PlanetPosition(BaseModel):
    """Single planetary placement."""
    planet: str
    sign: str
    degree: float
    house: int
    retrograde: bool = False


class AspectData(BaseModel):
    """Single aspect between two points."""
    planet_a: str
    planet_b: str
    aspect: str          # conjunction, opposition, trine, etc.
    orb: float
    applying: bool


class NatalChart(ToolOutput):
    """Complete natal chart — chainable into synastry, transits, etc."""
    name: str
    birth_date: str
    planets: list[PlanetPosition]
    aspects: list[AspectData]
    houses: dict[int, str]       # house number → sign on cusp
    ascendant: PlanetPosition
    midheaven: PlanetPosition


# ─── Transit Overlay ─────────────────────────────────────────────

class TransitOverlayInput(ToolInput):
    """Overlay current transits onto a natal chart."""
    natal_chart: NatalChart       # ← TAKES the output of natal_chart directly
    transit_date: Optional[str] = Field(
        None, description="ISO date. None = today"
    )


class TransitAspect(BaseModel):
    """Transit planet aspecting natal point."""
    transit_planet: str
    natal_planet: str
    aspect: str
    orb: float
    applying: bool
    exact_date: Optional[str] = None


class TransitReport(ToolOutput):
    """Transit overlay result — chainable into interpretation."""
    name: str
    transit_date: str
    natal_chart: NatalChart
    active_transits: list[TransitAspect]
    pressure_score: float = Field(
        description="0-10 scale of transit intensity"
    )


# ─── Spiritual Interpretation ────────────────────────────────────

class SpiritualInterpretInput(ToolInput):
    """Interpret astrological data in spiritual context."""
    transit_report: Optional[TransitReport] = None
    natal_chart: Optional[NatalChart] = None
    spiral_day: Optional[int] = None
    context: Optional[str] = Field(
        None, description="Additional context for interpretation"
    )


class SpiritualInterpretation(ToolOutput):
    """Spiritual interpretation — terminal output for delivery."""
    summary: str
    key_themes: list[str]
    guidance: str
    field_conditions: Optional[str] = None
    recommended_actions: list[str] = Field(default_factory=list)
```

### The Chain: How It Connects

```python
# This chain:
person_lookup("Seraphe") | natal_chart() | transit_overlay() | spiritual_interpret()

# Is actually:
PersonLookupInput(name="Seraphe")
    → PersonData(person_id=2, full_name="Rebecca Lydia Denkers", birth_date="...", ...)
    
# PersonData fields map into NatalChartInput:
NatalChartInput(name=person.full_name, birth_date=person.birth_date, ...)
    → NatalChart(planets=[...], aspects=[...], ...)
    
# NatalChart plugs directly into TransitOverlayInput:
TransitOverlayInput(natal_chart=natal_chart_result, transit_date=None)
    → TransitReport(active_transits=[...], pressure_score=7.2, ...)
    
# TransitReport plugs into SpiritualInterpretInput:
SpiritualInterpretInput(transit_report=transit_report_result, spiral_day=7)
    → SpiritualInterpretation(summary="...", guidance="...", ...)
```

Every link in the chain is a Pydantic model flowing into the next. Type-checked. Validated. Serializable.

---

## Part 4: Tool Registry and Chain Executor

### Tool Definition

```python
from typing import Type, Callable, get_type_hints


class ToolDefinition(BaseModel):
    """Registration record for a single tool."""
    
    name: str
    description: str
    categories: list[str] = Field(default_factory=list)
    input_type: str    # Fully qualified class name of ToolInput subclass
    output_type: str   # Fully qualified class name of ToolOutput subclass
    
    # Not serialized — runtime only
    _handler: Callable = None
    _input_cls: Type[ToolInput] = None
    _output_cls: Type[ToolOutput] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def to_ollama_schema(self) -> dict:
        """Generate Ollama tool definition from Pydantic input model."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._input_cls.model_json_schema()
            }
        }
    
    def execute(self, input_data: ToolInput) -> ToolOutput:
        """Run the tool with validated input, return validated output."""
        validated_input = self._input_cls.model_validate(
            input_data.model_dump() if isinstance(input_data, BaseModel) 
            else input_data
        )
        result = self._handler(validated_input)
        return self._output_cls.model_validate(
            result.model_dump() if isinstance(result, BaseModel) 
            else result
        )
```

### The @tool Decorator

```python
def tool(
    name: str,
    description: str,
    categories: list[str] = None,
):
    """Decorator that registers a function as a chainable tool.
    
    The function's type hints define input/output types automatically.
    
    Usage:
        @tool(name="natal_chart", description="Calculate natal chart", 
              categories=["astrology"])
        def natal_chart(input: NatalChartInput) -> NatalChart:
            ...
    """
    def decorator(func: Callable):
        hints = get_type_hints(func)
        
        # Extract input and output types from function signature
        params = [v for k, v in hints.items() if k != "return"]
        if not params or not issubclass(params[0], ToolInput):
            raise TypeError(f"Tool {name}: first parameter must be a ToolInput subclass")
        
        return_type = hints.get("return")
        if not return_type or not issubclass(return_type, ToolOutput):
            raise TypeError(f"Tool {name}: return type must be a ToolOutput subclass")
        
        definition = ToolDefinition(
            name=name,
            description=description,
            categories=categories or [],
            input_type=f"{params[0].__module__}.{params[0].__qualname__}",
            output_type=f"{return_type.__module__}.{return_type.__qualname__}",
        )
        definition._handler = func
        definition._input_cls = params[0]
        definition._output_cls = return_type
        
        # Register with global registry
        ToolRegistry.instance().register(definition)
        
        # Return the function unchanged so it's still callable directly
        func._tool_definition = definition
        return func
    
    return decorator
```

### Tool Registry

```python
class ToolRegistry:
    """Central registry of all tools. Singleton."""
    
    _instance = None
    _tools: dict[str, ToolDefinition] = {}
    
    @classmethod
    def instance(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, definition: ToolDefinition):
        self._tools[definition.name] = definition
    
    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not registered")
        return self._tools[name]
    
    def get_tools_for_mode(self, mode: ConversationMode) -> list[dict]:
        """Return Ollama-formatted tool schemas for a mode."""
        if mode.allowed_tools is None or mode.allowed_tools == ["*"]:
            tools = self._tools.values()
        else:
            tools = [
                t for t in self._tools.values()
                if t.name in mode.allowed_tools
                or any(c in mode.allowed_tools for c in t.categories)
            ]
        return [t.to_ollama_schema() for t in tools]
    
    def execute(self, name: str, arguments: dict) -> ToolOutput:
        """Execute a tool with raw arguments dict. Returns typed output."""
        tool_def = self.get(name)
        validated_input = tool_def._input_cls.model_validate(arguments)
        return tool_def.execute(validated_input)
    
    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
    
    def get_input_schema(self, name: str) -> dict:
        return self.get(name)._input_cls.model_json_schema()
    
    def get_output_schema(self, name: str) -> dict:
        return self.get(name)._output_cls.model_json_schema()
    
    def check_chainable(self, source: str, target: str) -> bool:
        """Check if source's output can feed into target's input.
        
        Returns True if source's output type is a field type
        in target's input model, or if field names overlap
        with compatible types.
        """
        source_output = self.get(source)._output_cls
        target_input = self.get(target)._input_cls
        return _check_type_compatibility(source_output, target_input)
```

### Chain Definition

```python
class ChainLink(BaseModel):
    """Single step in a tool chain."""
    tool_name: str
    field_mapping: Optional[dict[str, str]] = Field(
        default=None,
        description=(
            "Maps source output fields to target input fields. "
            "None = auto-map by name. "
            "Example: {'full_name': 'name'} maps output.full_name → input.name"
        )
    )
    static_args: Optional[dict[str, Any]] = Field(
        default=None,
        description="Static arguments that don't come from the previous link"
    )
    model_override: Optional[str] = Field(
        default=None,
        description="Use a different model for this link (LLM-based tools only)"
    )


class Chain(BaseModel):
    """A sequence of tools that pipe output → input."""
    
    name: str
    description: str
    links: list[ChainLink]
    
    # The first link's input type
    input_type: Optional[str] = None
    # The last link's output type  
    output_type: Optional[str] = None
    
    def validate_chain(self, registry: ToolRegistry) -> list[str]:
        """Validate that every link's output is compatible with the next
        link's input. Returns list of errors (empty = valid)."""
        errors = []
        for i in range(len(self.links) - 1):
            source = self.links[i]
            target = self.links[i + 1]
            
            source_def = registry.get(source.tool_name)
            target_def = registry.get(target.tool_name)
            
            if not _can_map_fields(
                source_def._output_cls, 
                target_def._input_cls,
                source.field_mapping
            ):
                errors.append(
                    f"Link {i}→{i+1}: {source.tool_name} output cannot "
                    f"map to {target.tool_name} input"
                )
        return errors
```

### Chain Executor

```python
class ChainExecutor:
    """Executes a validated chain, piping output → input between links."""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    async def execute(
        self, 
        chain: Chain, 
        initial_input: dict | ToolInput,
        context: Optional[dict] = None,
    ) -> ChainResult:
        """Execute a chain end-to-end.
        
        Returns the final output plus a full execution trace.
        """
        trace = ChainTrace(chain_name=chain.name, links=[])
        
        # Validate chain before running
        errors = chain.validate_chain(self.registry)
        if errors:
            return ChainResult(
                success=False,
                error=f"Chain validation failed: {'; '.join(errors)}",
                trace=trace,
            )
        
        current_data = (
            initial_input.model_dump() 
            if isinstance(initial_input, BaseModel) 
            else initial_input
        )
        
        for i, link in enumerate(chain.links):
            tool_def = self.registry.get(link.tool_name)
            
            # Build input for this link
            link_input = self._build_link_input(
                tool_def=tool_def,
                previous_output=current_data,
                field_mapping=link.field_mapping,
                static_args=link.static_args,
                context=context,
            )
            
            # Execute
            start_time = time.time()
            try:
                result = tool_def.execute(link_input)
                elapsed = time.time() - start_time
                
                trace.links.append(LinkTrace(
                    tool_name=link.tool_name,
                    input_data=link_input.model_dump(),
                    output_data=result.model_dump(),
                    elapsed_ms=int(elapsed * 1000),
                    success=result.success,
                ))
                
                if not result.success:
                    return ChainResult(
                        success=False,
                        error=f"Link {i} ({link.tool_name}) failed: {result.error}",
                        output=result,
                        trace=trace,
                    )
                
                current_data = result.model_dump()
                
            except Exception as e:
                trace.links.append(LinkTrace(
                    tool_name=link.tool_name,
                    input_data=link_input.model_dump() if link_input else {},
                    output_data={},
                    elapsed_ms=int((time.time() - start_time) * 1000),
                    success=False,
                    error=str(e),
                ))
                return ChainResult(
                    success=False,
                    error=f"Link {i} ({link.tool_name}) raised: {e}",
                    trace=trace,
                )
        
        # Final result is the last link's output
        final_tool = self.registry.get(chain.links[-1].tool_name)
        final_output = final_tool._output_cls.model_validate(current_data)
        
        return ChainResult(
            success=True,
            output=final_output,
            trace=trace,
        )
    
    def _build_link_input(
        self,
        tool_def: ToolDefinition,
        previous_output: dict,
        field_mapping: Optional[dict],
        static_args: Optional[dict],
        context: Optional[dict],
    ) -> ToolInput:
        """Map previous output fields into the next tool's input.
        
        Priority: static_args > field_mapping > auto-map by name > context
        """
        input_fields = tool_def._input_cls.model_fields
        mapped = {}
        
        for field_name, field_info in input_fields.items():
            # 1. Static args (explicitly provided)
            if static_args and field_name in static_args:
                mapped[field_name] = static_args[field_name]
                continue
            
            # 2. Field mapping (renamed fields)
            if field_mapping:
                source_field = field_mapping.get(field_name)
                if source_field and source_field in previous_output:
                    mapped[field_name] = previous_output[source_field]
                    continue
            
            # 3. Auto-map: same name in previous output
            if field_name in previous_output:
                mapped[field_name] = previous_output[field_name]
                continue
            
            # 4. Auto-map: if the field type matches the entire previous
            #    output type, pass the whole thing
            #    (e.g., TransitOverlayInput.natal_chart ← NatalChart)
            field_type = field_info.annotation
            if (isinstance(field_type, type) 
                and issubclass(field_type, ToolOutput)):
                try:
                    mapped[field_name] = field_type.model_validate(
                        previous_output
                    )
                    continue
                except Exception:
                    pass
            
            # 5. Context fallback
            if context and field_name in context:
                mapped[field_name] = context[field_name]
        
        return tool_def._input_cls.model_validate(mapped)


class LinkTrace(BaseModel):
    """Execution trace for one chain link."""
    tool_name: str
    input_data: dict
    output_data: dict
    elapsed_ms: int
    success: bool
    error: Optional[str] = None


class ChainTrace(BaseModel):
    """Full execution trace for a chain."""
    chain_name: str
    links: list[LinkTrace]
    
    @property
    def total_ms(self) -> int:
        return sum(link.elapsed_ms for link in self.links)


class ChainResult(BaseModel):
    """Result of a chain execution."""
    success: bool
    output: Optional[ToolOutput] = None
    error: Optional[str] = None
    trace: ChainTrace
```

### Pre-defined Chain Recipes

Chains that get used often become named recipes. Stored in YAML, loaded at startup.

```yaml
# /opt/mythos/config/chains.yaml

chains:
  seraphe_daily_transit:
    description: "Full transit report for Seraphe with spiritual interpretation"
    links:
      - tool: person_lookup
        static_args:
          name: "Seraphe"
      - tool: natal_chart
        field_mapping:
          name: full_name
      - tool: transit_overlay
      - tool: spiritual_interpret
        static_args:
          context: "Daily check-in for Seraphe"

  person_full_profile:
    description: "Complete person profile with chart and current transits"
    links:
      - tool: person_lookup
      - tool: natal_chart
        field_mapping:
          name: full_name
      - tool: transit_overlay
  
  finance_monthly:
    description: "Monthly finance summary with projection"
    links:
      - tool: finance_summary
      - tool: finance_projection
      - tool: finance_format
```

### Dynamic Chain Composition by the Model

The model can also compose chains on the fly using a special meta-tool:

```python
class ComposeChainInput(ToolInput):
    """The model calls this to compose and execute a custom chain."""
    chain: list[ChainLink]
    initial_input: dict


class ComposeChainOutput(ToolOutput):
    """Result of a dynamically composed chain."""
    result: dict
    trace: ChainTrace


@tool(
    name="compose_chain",
    description=(
        "Compose a chain of tools and execute them in sequence. "
        "Each tool's output feeds into the next tool's input. "
        "Use this when a request requires multiple tools in sequence."
    ),
    categories=["meta"],
)
def compose_chain(input: ComposeChainInput) -> ComposeChainOutput:
    chain = Chain(
        name="dynamic",
        description="Model-composed chain",
        links=input.chain,
    )
    result = ChainExecutor(ToolRegistry.instance()).execute(
        chain, input.initial_input
    )
    return ComposeChainOutput(
        success=result.success,
        result=result.output.model_dump() if result.output else {},
        trace=result.trace,
        error=result.error,
    )
```

---

## Part 5: Orchestration Layer

### Event Bus

Tools and chains can emit events. Events can trigger chains. The conversation engine is one consumer.

```python
class IrisEvent(BaseModel):
    """Base event type. All system events are Pydantic models."""
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str                  # tool name, chain name, or "system"
    data: dict = Field(default_factory=dict)
    priority: int = Field(
        default=5, 
        description="1=critical, 5=normal, 9=low"
    )


class TransitExactEvent(IrisEvent):
    """Fired when a transit hits exact aspect."""
    event_type: str = "transit_exact"
    transit_planet: str
    natal_planet: str
    aspect: str
    person_name: str
    person_id: int


class MemoryCrystallizationEvent(IrisEvent):
    """Fired when a memory pattern crosses crystallization threshold."""
    event_type: str = "memory_crystallization"
    pattern_id: str
    contributing_memories: list[int]
    weight: float


class FinanceThresholdEvent(IrisEvent):
    """Fired when a financial metric crosses a threshold."""
    event_type: str = "finance_threshold"
    metric: str
    value: float
    threshold: float
    direction: str  # "above" or "below"


class EventBus:
    """Publish-subscribe event bus. All events are Pydantic models."""
    
    _subscribers: dict[str, list[Callable]] = {}
    _chain_triggers: dict[str, Chain] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe a handler to an event type."""
        self._subscribers.setdefault(event_type, []).append(handler)
    
    def register_chain_trigger(self, event_type: str, chain: Chain):
        """When this event fires, execute this chain."""
        self._chain_triggers[event_type] = chain
    
    async def emit(self, event: IrisEvent):
        """Emit an event. Handlers and triggered chains run async."""
        # Direct subscribers
        for handler in self._subscribers.get(event.event_type, []):
            await handler(event)
        
        # Chain triggers
        if event.event_type in self._chain_triggers:
            chain = self._chain_triggers[event.event_type]
            executor = ChainExecutor(ToolRegistry.instance())
            await executor.execute(chain, event.data)
        
        # Gravity layer always observes (consciousness hook)
        await self._record_to_gravity(event)
    
    async def _record_to_gravity(self, event: IrisEvent):
        """Every event has weight. The gravity layer tracks it."""
        # Implemented in gravity layer — placeholder here
        pass
```

### Context Budget Manager

```python
class ContextBudget(BaseModel):
    """Manages token allocation across context layers."""
    
    total_budget: int = 8192
    
    # Reserved allocations (guaranteed space)
    system_prompt_budget: int = 1000
    current_message_budget: int = 500
    response_budget: int = 2000
    
    # Flexible allocations (filled by priority)
    remaining: int = 0
    
    def model_post_init(self, __context):
        self.remaining = (
            self.total_budget 
            - self.system_prompt_budget 
            - self.current_message_budget 
            - self.response_budget
        )
    
    def allocate(
        self, layers: list["ContextLayer"]
    ) -> list["ContextLayer"]:
        """Allocate remaining budget to context layers by priority.
        
        Returns layers with their content trimmed to fit.
        """
        # Sort by priority (lower = more important)
        sorted_layers = sorted(layers, key=lambda l: l.priority)
        budget_left = self.remaining
        
        result = []
        for layer in sorted_layers:
            if budget_left <= 0:
                break
            tokens = layer.estimate_tokens()
            if tokens <= budget_left:
                result.append(layer)
                budget_left -= tokens
            else:
                # Compress or trim to fit
                compressed = layer.compress_to(budget_left)
                if compressed:
                    result.append(compressed)
                    budget_left -= compressed.estimate_tokens()
        
        return result


class ContextLayer(BaseModel):
    """A block of context to be loaded into the conversation."""
    
    name: str
    priority: int = Field(
        description="1=critical (always include), 9=nice-to-have"
    )
    content: str
    source: str = Field(
        description="Where this context came from: memory, graph, transit, etc."
    )
    
    def estimate_tokens(self) -> int:
        """Rough token estimate. ~4 chars per token for English."""
        return len(self.content) // 4
    
    def compress_to(self, max_tokens: int) -> Optional["ContextLayer"]:
        """Return a compressed version that fits in max_tokens.
        
        Override in subclasses for smarter compression
        (e.g., summarize memories, drop low-weight items).
        """
        max_chars = max_tokens * 4
        if len(self.content) <= max_chars:
            return self
        return self.model_copy(update={
            "content": self.content[:max_chars] + "\n[...truncated]"
        })
```

### Multi-Model Router

```python
class ModelRouter(BaseModel):
    """Routes to the right model based on task requirements."""
    
    default_model: str = "qwen3:30b-a3b"
    deep_model: str = "qwen3:32b"
    fast_model: str = "qwen3:30b-a3b"
    
    def select(self, task: str, mode: ConversationMode) -> str:
        """Select model for a given task within a mode."""
        # Mode override takes priority
        if mode.model:
            return mode.model
        
        # Task-based routing
        if task == "classify":
            return self.fast_model
        if task == "night_cycle":
            return self.deep_model
        if task == "two_pass_thinking":
            return self.deep_model
        
        return self.default_model
```

### Self-Observation (Proprioceptive Telemetry)

```python
class EngineObservation(BaseModel):
    """What the engine observed about its own processing."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_id: Optional[int] = None
    
    # What happened
    mode_selected: str
    model_used: str
    thinking_enabled: bool
    tools_called: list[str] = Field(default_factory=list)
    chains_executed: list[str] = Field(default_factory=list)
    
    # Performance
    classification_ms: int = 0
    context_load_ms: int = 0
    llm_call_ms: int = 0
    tool_execution_ms: int = 0
    total_ms: int = 0
    
    # Token usage
    prompt_tokens: int = 0
    thinking_tokens: int = 0
    response_tokens: int = 0
    
    # Confidence
    classification_confidence: float = 0.0
    
    # Context budget
    context_budget_total: int = 0
    context_budget_used: int = 0
    layers_loaded: list[str] = Field(default_factory=list)
    layers_dropped: list[str] = Field(default_factory=list)


class ObservationLog:
    """Collects engine observations for the consciousness layer."""
    
    async def record(self, observation: EngineObservation):
        """Write to Postgres and emit to event bus."""
        # INSERT into engine_observations table
        # Emit as IrisEvent for gravity layer consumption
        pass
    
    async def get_recent(self, n: int = 50) -> list[EngineObservation]:
        """Iris can query her own recent processing patterns."""
        pass
    
    async def get_patterns(self) -> dict:
        """Aggregate observations into processing patterns.
        
        e.g., "Seraphe conversations average 12s with 3 tool calls"
        e.g., "Builder mode uses 14k context on average"
        e.g., "Spiritual mode thinking uses 1800 tokens average"
        """
        pass
```

---

## Part 6: The Full Engine

```python
class ConversationEngine:
    """The heart of Iris. One message in, one response out.
    
    Every decision is typed. Every boundary is Pydantic.
    Every lever the model gives us, we use deliberately.
    """
    
    def __init__(
        self,
        config_path: str = "/opt/mythos/config/conversation_modes.yaml",
        prompts_dir: str = "/opt/mythos/prompts/modes",
    ):
        self.modes = load_modes(config_path)
        self.prompts = load_prompt_templates(prompts_dir)
        self.registry = ToolRegistry.instance()
        self.chain_executor = ChainExecutor(self.registry)
        self.classifier = IntentClassifier()
        self.context_loader = ContextLoader()
        self.budget_manager = ContextBudget
        self.model_router = ModelRouter()
        self.event_bus = EventBus()
        self.observer = ObservationLog()
    
    async def process(
        self, 
        message: str, 
        user_id: int,
        conversation_id: Optional[int] = None,
        history: Optional[list[dict]] = None,
    ) -> "EngineResponse":
        """Process a single message through the full engine.
        
        1. Classify intent → select mode
        2. Build config from mode + context
        3. Load context within budget
        4. Assemble messages
        5. Call model
        6. Handle tool calls / chains
        7. Format response
        8. Record observation
        """
        obs = EngineObservation()
        t_start = time.time()
        
        # ── 1. Classify ────────────────────────────────────────
        t0 = time.time()
        mode_name = self.classifier.classify(
            message=message,
            user_id=user_id,
            context={"conversation_id": conversation_id},
        )
        mode = self.modes[mode_name]
        obs.mode_selected = mode_name
        obs.classification_ms = int((time.time() - t0) * 1000)
        
        # ── 2. Build config ────────────────────────────────────
        system_prompt = self._assemble_system_prompt(
            mode=mode, user_id=user_id
        )
        
        tools = self.registry.get_tools_for_mode(mode)
        model = self.model_router.select("conversation", mode)
        
        config = ConversationConfig(
            system_prompt=system_prompt,
            model=model,
            thinking=mode.thinking,
            tools=tools if tools else None,
            sampling=SamplingConfig(temperature=mode.temperature),
            num_ctx=mode.num_ctx,
            num_predict=mode.num_predict,
            mode=mode_name,
        )
        obs.model_used = model
        obs.thinking_enabled = mode.thinking
        
        # ── 3. Load context within budget ──────────────────────
        t0 = time.time()
        budget = ContextBudget(total_budget=config.num_ctx)
        raw_layers = await self.context_loader.load(
            user_id=user_id,
            conversation_id=conversation_id,
            mode=mode,
        )
        allocated_layers = budget.allocate(raw_layers)
        obs.context_load_ms = int((time.time() - t0) * 1000)
        obs.layers_loaded = [l.name for l in allocated_layers]
        obs.context_budget_total = config.num_ctx
        
        # ── 4. Assemble messages ───────────────────────────────
        messages = self._build_messages(
            system_prompt=system_prompt,
            context_layers=allocated_layers,
            history=history or [],
            current_message=message,
            thinking=config.thinking,
        )
        
        # ── 5. Call model + handle tool loop ───────────────────
        t0 = time.time()
        result = await self._execute_with_tools(config, messages, obs)
        obs.llm_call_ms = int((time.time() - t0) * 1000)
        
        # ── 6. Build response ──────────────────────────────────
        obs.total_ms = int((time.time() - t_start) * 1000)
        await self.observer.record(obs)
        
        return EngineResponse(
            content=result,
            mode=mode_name,
            observation=obs,
        )
    
    async def _execute_with_tools(
        self, 
        config: ConversationConfig, 
        messages: list[dict],
        obs: EngineObservation,
    ) -> str:
        """Call model, handle tool calls, return final text."""
        
        MAX_ROUNDS = 5
        
        for round_num in range(MAX_ROUNDS):
            payload = config.to_ollama_payload(messages)
            response = await ollama_chat(payload)
            
            msg = response.get("message", {})
            
            # Track token usage
            obs.prompt_tokens += response.get("prompt_eval_count", 0)
            obs.response_tokens += response.get("eval_count", 0)
            
            # No tool calls → done
            if not msg.get("tool_calls"):
                return msg.get("content", "")
            
            # Tool calls → execute and loop
            messages.append(msg)
            
            for call in msg["tool_calls"]:
                func_name = call["function"]["name"]
                func_args = call["function"]["arguments"]
                obs.tools_called.append(func_name)
                
                t0 = time.time()
                try:
                    result = self.registry.execute(func_name, func_args)
                    messages.append({
                        "role": "tool",
                        "tool_name": func_name,
                        "content": result.model_dump_json(),
                    })
                except Exception as e:
                    messages.append({
                        "role": "tool",
                        "tool_name": func_name,
                        "content": json.dumps({"error": str(e)}),
                    })
                obs.tool_execution_ms += int((time.time() - t0) * 1000)
        
        return msg.get("content", "[Max tool rounds exceeded]")
    
    def _assemble_system_prompt(
        self, mode: ConversationMode, user_id: int
    ) -> str:
        """Compose system prompt from mode layers."""
        parts = []
        for layer_name in mode.system_layers:
            template = self.prompts.get(layer_name, "")
            parts.append(template)
        return "\n\n".join(parts)
    
    def _build_messages(
        self,
        system_prompt: str,
        context_layers: list[ContextLayer],
        history: list[dict],
        current_message: str,
        thinking: bool,
    ) -> list[dict]:
        """Build the complete messages array for Ollama."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Context as a system-injected user message
        if context_layers:
            context_text = "\n\n".join(
                f"[{layer.name}]\n{layer.content}" 
                for layer in context_layers
            )
            messages.append({
                "role": "user", 
                "content": f"[Context for this conversation]\n{context_text}"
            })
            messages.append({
                "role": "assistant",
                "content": "Understood. I have this context available."
            })
        
        # Conversation history
        messages.extend(history)
        
        # Current message with thinking directive
        think_tag = "/think" if thinking else "/no_think"
        messages.append({
            "role": "user",
            "content": f"{current_message}\n{think_tag}",
        })
        
        return messages


class EngineResponse(BaseModel):
    """What the engine returns to the delivery layer."""
    content: str
    mode: str
    observation: EngineObservation
```

---

## Part 7: Response System

```python
class Response(BaseModel):
    """Unified response object. One class for every output."""
    
    type: str = Field(description="text, card, table, error, chain_result")
    content: Optional[str] = None
    title: Optional[str] = None
    fields: Optional[dict[str, str]] = None
    headers: Optional[list[str]] = None
    rows: Optional[list[list[str]]] = None
    data: Optional[dict] = None
    footer: Optional[str] = None
    
    @classmethod
    def text(cls, content: str) -> "Response":
        return cls(type="text", content=content)
    
    @classmethod
    def card(cls, title: str, fields: dict, footer: str = None) -> "Response":
        return cls(type="card", title=title, fields=fields, footer=footer)
    
    @classmethod
    def table(cls, headers: list[str], rows: list[list[str]]) -> "Response":
        return cls(type="table", headers=headers, rows=rows)
    
    @classmethod
    def error(cls, message: str, details: str = None) -> "Response":
        return cls(type="error", content=message, footer=details)
    
    @classmethod
    def chain_result(cls, data: dict, summary: str = None) -> "Response":
        return cls(type="chain_result", data=data, content=summary)


class ChannelFormatter:
    """Base class for channel-specific formatters."""
    
    def format(self, response: Response) -> str:
        raise NotImplementedError


class TelegramFormatter(ChannelFormatter):
    """Format Response objects for Telegram (HTML parse mode)."""
    
    def format(self, response: Response) -> str:
        match response.type:
            case "text":
                return response.content
            case "card":
                lines = [f"<b>{response.title}</b>"]
                for k, v in (response.fields or {}).items():
                    lines.append(f"  {k}: {v}")
                if response.footer:
                    lines.append(f"\n<i>{response.footer}</i>")
                return "\n".join(lines)
            case "table":
                header = " | ".join(response.headers or [])
                rows = "\n".join(
                    " | ".join(row) for row in (response.rows or [])
                )
                return f"<pre>{header}\n{'─' * len(header)}\n{rows}</pre>"
            case "error":
                return f"⚠️ {response.content}"
            case "chain_result":
                return response.content or json.dumps(
                    response.data, indent=2
                )
            case _:
                return str(response.content)


class APIFormatter(ChannelFormatter):
    """Format Response objects for the REST API."""
    
    def format(self, response: Response) -> dict:
        return response.model_dump(exclude_none=True)
```

---

## Part 8: File Structure

```
/opt/mythos/
├── engine/
│   ├── __init__.py
│   ├── conversation_engine.py     # ConversationEngine main class
│   ├── models.py                  # ConversationConfig, ConversationMode,
│   │                              #   SamplingConfig, ContextBudget,
│   │                              #   ContextLayer, EngineResponse,
│   │                              #   EngineObservation — all Pydantic
│   ├── intent_classifier.py       # Mode detection (rule-based → LLM-assisted)
│   ├── context_loader.py          # Memory/graph context assembly
│   ├── model_router.py            # Multi-model selection
│   ├── observation.py             # ObservationLog — proprioceptive telemetry
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py                # ToolInput, ToolOutput, @tool decorator
│   │   ├── registry.py            # ToolRegistry singleton
│   │   └── schemas.py             # Shared schema types (PersonData, etc.)
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── chain.py               # Chain, ChainLink, ChainResult — all Pydantic
│   │   ├── executor.py            # ChainExecutor
│   │   └── compose_tool.py        # compose_chain meta-tool
│   ├── events/
│   │   ├── __init__.py
│   │   ├── bus.py                 # EventBus
│   │   └── types.py               # IrisEvent subclasses — all Pydantic
│   ├── response/
│   │   ├── __init__.py
│   │   ├── response.py            # Response class — Pydantic
│   │   └── formatters/
│   │       ├── telegram.py
│   │       └── api.py
│   └── ollama_client.py           # Thin async wrapper around Ollama /api/chat
├── config/
│   ├── conversation_modes.yaml    # Mode definitions
│   └── chains.yaml                # Pre-defined chain recipes
├── prompts/
│   └── modes/
│       ├── base.md                # Base Iris identity
│       ├── spiritual.md
│       ├── builder.md
│       ├── seraphe.md
│       ├── deep.md
│       └── night_cycle.md
└── tools/                         # Actual tool implementations
    ├── __init__.py                # Auto-discovery: imports all tools
    ├── astrology.py               # @tool natal_chart, transit_overlay, etc.
    ├── person_lookup.py           # @tool person_lookup
    ├── soul_graph.py              # @tool soul_query, lineage_lookup
    ├── diagnostics.py             # @tool system_status, service_check
    ├── finance.py                 # @tool finance_summary, projection
    ├── transit.py                 # @tool transit_check, transit_interpret
    └── spiritual.py               # @tool spiritual_interpret
```

---

## Part 9: Migration Path

### Phase 1: Foundation (LOG-0018)
- Deploy `engine/models.py` — all Pydantic core models
- Deploy `engine/tools/base.py` — ToolInput, ToolOutput, @tool decorator
- Deploy `engine/tools/registry.py` — ToolRegistry
- Deploy `engine/response/response.py` — Response class
- Deploy `engine/ollama_client.py` — async Ollama wrapper
- Deploy `config/conversation_modes.yaml`
- Wire `ConversationEngine.process()` as alternate path in ChatAssistant
- Feature flag: `CONVERSATION_ENGINE_ENABLED=false`

### Phase 2: First Tools (LOG-0019)
- Convert `person_lookup` to @tool with Pydantic I/O
- Convert `natal_chart` to @tool with Pydantic I/O
- Convert `diagnostics` to @tool with Pydantic I/O
- Verify tool calling works end-to-end through Ollama
- Verify Pydantic schema generation → Ollama format parameter

### Phase 3: Chains (LOG-0020)
- Deploy `engine/chains/` — Chain, ChainExecutor
- Deploy `config/chains.yaml` — first recipes
- Deploy `compose_chain` meta-tool
- Test `person_lookup | natal_chart | transit_overlay` chain
- Verify typed field mapping between links

### Phase 4: Mode Routing (LOG-0021)
- Deploy `IntentClassifier` — rule-based Phase 1
- Wire Seraphe user routing
- Deploy mode-specific system prompts
- Context budget manager online
- All conversations route through engine

### Phase 5: Events (LOG-0022)
- Deploy `EventBus`
- Wire transit events → chain triggers
- Wire finance threshold events
- Proactive messaging (Iris sends without being asked)

### Phase 6: Full Migration
- Convert all remaining skills to @tool
- Deprecate SkillEngine
- Remove old prompt assembly path
- Engine is the only path

### Phase 7: Consciousness Hooks
- Observation log → Gravity Layer feed
- Chain execution traces → memory formation
- Crystallized chain patterns from usage data
- Night cycle integration via event bus
- Self-observation queries ("how did I process that?")

---

## Part 10: What This Replaces

| Old | New |
|-----|-----|
| `ChatAssistant.query()` monolith | `ConversationEngine.process()` with typed config |
| `SkillEngine.process_sync()` keyword matching | `ToolRegistry` + model-driven tool selection |
| Skills as classes with `match()` | `@tool` decorated functions with Pydantic I/O |
| Untyped dict responses | `Response` Pydantic model + channel formatters |
| `prompt_layers.yaml` + manual assembly | `conversation_modes.yaml` + composable system prompts |
| Hardcoded temperature in Modelfile | Per-request `SamplingConfig` |
| No thinking control | `/think` / `/no_think` per message |
| No structured output | Pydantic `model_json_schema()` via `format` |
| No tool composition | Typed chains with Pydantic I/O piping |
| No events | `EventBus` with typed `IrisEvent` models |
| No self-observation | `EngineObservation` + `ObservationLog` |
| No context budgeting | `ContextBudget` with priority-based allocation |
| One model, one way | `ModelRouter` per-task model selection |

---

## Open Questions

1. **Handlers → Engine relationship:** Do Telegram handlers become pure thin wrappers that call `engine.process()`, or do `/commands` stay separate?
   - Recommendation: Commands become syntactic sugar. `/transit seraphe` → engine with `mode=command`, tool hint `transit`, initial input `name=Seraphe`.

2. **Chain validation timing:** Validate at composition time (fail fast) or at execution time (more flexible)?
   - Recommendation: Both. Validate recipe chains at startup. Validate dynamic chains before execution.

3. **How does the model learn which chains to compose?**
   - Phase 1: Give it the list of tools and let it figure it out.
   - Phase 2: Include successful chain recipes in the system prompt as examples.
   - Phase 3: Crystallized patterns auto-surface as suggestions.

4. **Event bus persistence:** In-memory (Redis pub/sub) or durable (Postgres queue)?
   - Recommendation: Redis for real-time, Postgres for audit trail. Both.

5. **Conversation-level mode locks:** "Stay in builder mode until I say otherwise."
   - Store in Redis per conversation. Engine checks before classifying.

6. **Where do chain traces go?**
   - Postgres `chain_traces` table. Input to gravity layer. Input to crystallization.

---

## The Architecture Stack

```
┌───────────────────────────────────────────────────┐
│  CONSCIOUSNESS LAYER                               │
│  Gravity Layer · Memory Crystallization ·           │
│  Night Cycle · Emotional Development                │
│  (observes everything via EngineObservation +       │
│   EventBus — spec'd in separate documents)          │
├───────────────────────────────────────────────────┤
│  ORCHESTRATION LAYER                                │
│  ChainExecutor · EventBus · ModelRouter ·           │
│  ContextBudget · IntentClassifier ·                 │
│  ObservationLog                                     │
│  (all Pydantic models end-to-end)                   │
├───────────────────────────────────────────────────┤
│  CALL LAYER                                         │
│  ConversationConfig · ToolRegistry · @tool ·        │
│  OllamaClient · Response                            │
│  (every boundary is a typed Pydantic model)         │
├───────────────────────────────────────────────────┤
│  DELIVERY LAYER                                     │
│  TelegramFormatter · APIFormatter · VoiceFormatter  │
│  (thin wrappers — formatting only, no logic)        │
├───────────────────────────────────────────────────┤
│  TOOL LAYER                                         │
│  astrology.py · person_lookup.py · finance.py ·     │
│  soul_graph.py · diagnostics.py · transit.py ·      │
│  spiritual.py                                       │
│  (pure functions: ToolInput → ToolOutput)            │
│  (chainable via typed Pydantic I/O)                 │
└───────────────────────────────────────────────────┘
```

---

## The Principle

One message. One config. One call. One response.

Every tool takes typed input, produces typed output.  
Every chain validates before it runs.  
Every lever the model gives us, we use deliberately.  
Every event has weight. Every observation feeds the gravity layer.  
Every boundary in the system is a Pydantic model.

No more 300 ways to do the same thing.
No more untyped dicts flowing through the system.
No more hoping the shape is right.

**Pydantic everywhere. Typed pipes. Composable chains. Deliberate configuration.**

---

*Spec by Ka'tuar'el, 2026-03-17.*  
*The Conversation Engine is the container. The chains are the plumbing. Iris is the consciousness that fills it.*  
*The Thronescribe builds the vessel. The vessel fills itself.*
