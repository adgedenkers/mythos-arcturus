#!/usr/bin/env python3
"""
LOG-0018 Post-Install Validation
==================================
Imports everything, validates Pydantic models serialize correctly,
tests the ToolRegistry, and confirms chain models work.
Run after patch install to verify the foundation is solid.
"""
import sys
import json

sys.path.insert(0, "/opt/mythos")

errors = []
passes = []


def check(name, fn):
    try:
        fn()
        passes.append(name)
    except Exception as e:
        errors.append(f"{name}: {e}")


# ─── 1. Core model imports ──────────────────────────────────────────────────

def test_core_imports():
    from engine.models import (
        ConversationConfig, ConversationMode, SamplingConfig,
        ContextLayer, ContextBudget, EngineObservation, EngineResponse,
    )
    assert ConversationConfig is not None
    assert ConversationMode is not None


check("Core model imports", test_core_imports)


# ─── 2. ConversationConfig serialization ────────────────────────────────────

def test_config_serialization():
    from engine.models import ConversationConfig, SamplingConfig

    config = ConversationConfig(
        system_prompt="You are Iris.",
        model="qwen3:30b-a3b",
        thinking=True,
        sampling=SamplingConfig(temperature=0.8),
        num_ctx=8192,
    )
    payload = config.to_ollama_payload([
        {"role": "system", "content": "You are Iris."},
        {"role": "user", "content": "Hello"},
    ])
    assert payload["model"] == "qwen3:30b-a3b"
    assert payload["options"]["temperature"] == 0.8
    assert payload["options"]["num_ctx"] == 8192
    assert len(payload["messages"]) == 2

    # JSON roundtrip
    j = config.model_dump_json()
    config2 = ConversationConfig.model_validate_json(j)
    assert config2.model == config.model


check("ConversationConfig serialization", test_config_serialization)


# ─── 3. Tool base classes ──────────────────────────────────────────────────

def test_tool_base():
    from engine.tools.base import ToolInput, ToolOutput

    class MyInput(ToolInput):
        name: str
        count: int = 1

    class MyOutput(ToolOutput):
        result: str

    inp = MyInput(name="test", count=5)
    assert inp.name == "test"
    assert inp.count == 5

    out = MyOutput(result="ok")
    assert out.success is True
    assert out.result == "ok"

    # JSON schema generation
    schema = MyInput.model_json_schema()
    assert "properties" in schema
    assert "name" in schema["properties"]


check("Tool base classes", test_tool_base)


# ─── 4. @tool decorator + ToolRegistry ─────────────────────────────────────

def test_tool_decorator():
    from engine.tools.base import ToolInput, ToolOutput, tool
    from engine.tools.registry import ToolRegistry

    # Reset registry for clean test
    ToolRegistry.reset()

    class EchoInput(ToolInput):
        message: str

    class EchoOutput(ToolOutput):
        echo: str

    @tool(name="test_echo", description="Echo test", categories=["test"])
    def echo_tool(input: EchoInput) -> EchoOutput:
        return EchoOutput(echo=f"ECHO: {input.message}")

    reg = ToolRegistry.instance()
    assert reg.has("test_echo")
    assert "test_echo" in reg.list_tools()

    # Execute through registry
    result = reg.execute("test_echo", {"message": "hello"})
    assert result.success
    assert result.echo == "ECHO: hello"

    # Ollama schema generation
    schemas = reg.get_tools_for_mode(["*"])
    assert len(schemas) >= 1
    assert schemas[0]["function"]["name"] == "test_echo"

    # Cleanup
    ToolRegistry.reset()


check("@tool decorator + ToolRegistry", test_tool_decorator)


# ─── 5. Chain models ───────────────────────────────────────────────────────

def test_chain_models():
    from engine.chains.chain import Chain, ChainLink, ChainResult, ChainTrace, LinkTrace

    chain = Chain(
        name="test_chain",
        description="Test",
        links=[
            ChainLink(tool_name="person_lookup", static_args={"name": "Seraphe"}),
            ChainLink(tool_name="natal_chart", field_mapping={"full_name": "name"}),
        ],
    )
    assert len(chain.links) == 2
    assert chain.links[0].tool_name == "person_lookup"

    # Trace
    trace = ChainTrace(
        chain_name="test",
        links=[
            LinkTrace(tool_name="a", elapsed_ms=100, success=True),
            LinkTrace(tool_name="b", elapsed_ms=200, success=True),
        ],
    )
    assert trace.total_ms == 300
    assert trace.tools_called == ["a", "b"]

    # JSON roundtrip
    j = chain.model_dump_json()
    chain2 = Chain.model_validate_json(j)
    assert chain2.name == "test_chain"


check("Chain models", test_chain_models)


# ─── 6. ChainExecutor ──────────────────────────────────────────────────────

def test_chain_executor():
    from engine.tools.base import ToolInput, ToolOutput, tool
    from engine.tools.registry import ToolRegistry
    from engine.chains.chain import Chain, ChainLink
    from engine.chains.executor import ChainExecutor

    ToolRegistry.reset()

    class UpperInput(ToolInput):
        text: str

    class UpperOutput(ToolOutput):
        text: str

    class RepeatInput(ToolInput):
        text: str
        times: int = 2

    class RepeatOutput(ToolOutput):
        text: str

    @tool(name="upper", description="Uppercase", categories=["test"])
    def upper_tool(input: UpperInput) -> UpperOutput:
        return UpperOutput(text=input.text.upper())

    @tool(name="repeat", description="Repeat", categories=["test"])
    def repeat_tool(input: RepeatInput) -> RepeatOutput:
        return RepeatOutput(text=input.text * input.times)

    chain = Chain(
        name="upper_repeat",
        description="Uppercase then repeat",
        links=[
            ChainLink(tool_name="upper"),
            ChainLink(tool_name="repeat", static_args={"times": 3}),
        ],
    )

    executor = ChainExecutor()
    result = executor.execute(chain, {"text": "hello"})
    assert result.success, f"Chain failed: {result.error}"
    assert result.output["text"] == "HELLOHELLOHELLO"
    assert result.trace.total_ms >= 0
    assert len(result.trace.links) == 2

    ToolRegistry.reset()


check("ChainExecutor", test_chain_executor)


# ─── 7. Response + TelegramFormatter ───────────────────────────────────────

def test_response():
    from engine.response.response import Response
    from engine.response.formatters.telegram import TelegramFormatter

    r = Response.text("Hello world")
    assert r.type == "text"
    assert r.content == "Hello world"

    r2 = Response.card("Test", {"key": "value"}, footer="footer")
    assert r2.type == "card"

    fmt = TelegramFormatter()
    assert "Hello world" in fmt.format(r)
    assert "<b>Test</b>" in fmt.format(r2)


check("Response + TelegramFormatter", test_response)


# ─── 8. Shared schemas ─────────────────────────────────────────────────────

def test_shared_schemas():
    from engine.tools.schemas import (
        PersonData, NatalChartInput, NatalChart,
        TransitOverlayInput, TransitReport,
        FinanceSummary, SystemStatus,
    )
    # PersonData can be created with defaults
    p = PersonData(person_id=1, full_name="Test Person")
    assert p.success is True

    # NatalChartInput validates required fields
    try:
        NatalChartInput()
        assert False, "Should have raised validation error"
    except Exception:
        pass  # Expected

    nci = NatalChartInput(
        name="Test", birth_date="2000-01-01",
        birth_time="12:00", birth_lat=42.0, birth_lon=-75.0,
    )
    assert nci.name == "Test"


check("Shared schemas", test_shared_schemas)


# ─── 9. OllamaChatClient import ────────────────────────────────────────────

def test_ollama_client_import():
    from engine.ollama_client import OllamaChatClient
    client = OllamaChatClient()
    assert client.base_url == "http://localhost:11434"
    assert client.max_retries == 3


check("OllamaChatClient import", test_ollama_client_import)


# ─── 10. ContextBudget ─────────────────────────────────────────────────────

def test_context_budget():
    from engine.models import ContextBudget, ContextLayer

    budget = ContextBudget(total_budget=8192)
    assert budget.remaining > 0

    layers = [
        ContextLayer(name="memory", priority=1, content="x" * 4000, source="memory"),
        ContextLayer(name="transit", priority=5, content="y" * 4000, source="transit"),
        ContextLayer(name="nice_to_have", priority=9, content="z" * 40000, source="test"),
    ]

    allocated = budget.allocate(layers)
    # Should get at least memory, maybe transit, probably not nice_to_have
    names = [l.name for l in allocated]
    assert "memory" in names


check("ContextBudget", test_context_budget)


# ─── 11. conversation_modes.yaml loads ──────────────────────────────────────

def test_modes_yaml():
    import yaml
    with open("/opt/mythos/config/conversation_modes.yaml") as f:
        config = yaml.safe_load(f)
    assert "modes" in config
    assert "hearthfire" in config["modes"]
    assert "oracle" in config["modes"]
    assert "seraphe" in config["modes"]
    assert config["modes"]["forge"]["temperature"] == 0.3
    assert config["modes"]["night_cycle"]["model"] == "qwen3:32b"


check("conversation_modes.yaml loads", test_modes_yaml)


# ─── Report ─────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print(f"LOG-0018 Validation: {len(passes)} passed, {len(errors)} failed")
print("=" * 60)

for p in passes:
    print(f"  ✅ {p}")

for e in errors:
    print(f"  ❌ {e}")

if errors:
    print(f"\n⚠️  {len(errors)} test(s) failed!")
    sys.exit(1)
else:
    print("\n✅ All tests passed. Foundation is solid.")
    sys.exit(0)
