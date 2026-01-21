# Patch 0006: LLM Diagnostics Interface

## Overview

This patch integrates your local LLM (Ollama) with the graph logging system, enabling natural language system diagnostics. The LLM can query the Neo4j graph, trace failures, and explain system state in plain English.

## What This Patch Does

### Creates
- `/opt/mythos/llm_diagnostics/` - LLM diagnostics infrastructure
- MCP (Model Context Protocol) server exposing diagnostic tools
- Ollama model configuration for system diagnostics
- Conversation logging to Neo4j graph
- Natural language interface for system queries

### Features
- **Natural Language Queries**: Ask "why is my system slow?" and get intelligent answers
- **Graph-Powered Diagnostics**: LLM queries Neo4j for events, causality, system state
- **Conversation Logging**: All LLM interactions logged to graph for learning
- **Tool Integration**: LLM has access to system health, failure tracing, event queries
- **Read-Only**: This patch only adds diagnostic capabilities (no system changes)

## Prerequisites

- Patch 0005 installed and operational
- Ollama installed (script will check and guide installation if needed)

## Installation

```bash
# Extract the patch
cd ~/Downloads
unzip patch_0006_llm_diagnostics.zip
cd patch_0006_build

# Run installation
./install.sh

# Or use pa command
pa 6
```

## What Gets Installed

### 1. MCP Server
- Location: `/opt/mythos/llm_diagnostics/mcp_server/`
- Exposes diagnostic functions as tools for LLM
- Runs as systemd service: `mythos-mcp-server`

### 2. Ollama Model
- Default model: `llama3.2:3b` (lightweight, fast)
- Configured with system diagnostics knowledge
- Custom system prompt for R2-D2 style responses

### 3. CLI Interface
- Command: `mythos-ask "your question"`
- Examples:
  - `mythos-ask "what's the system health?"`
  - `mythos-ask "why did neo4j backup fail?"`
  - `mythos-ask "show me recent errors"`

### 4. Conversation Logging
- All conversations logged to Neo4j
- Tracks: questions, answers, tool usage, accuracy
- Enables pattern learning over time

## Usage

### Basic Queries

```bash
# Check system health
mythos-ask "how is the system doing?"

# Trace a failure
mythos-ask "why did the backup fail?"

# Get recent events
mythos-ask "what happened in the last hour?"

# Service status
mythos-ask "is neo4j running?"

# Process information
mythos-ask "what's using the most memory?"
```

### Interactive Mode

```bash
# Start interactive session
mythos-chat

# Or with specific model
mythos-chat --model llama3.2:3b
```

### Python API

```python
from mythos_diagnostics import ask_system

# Ask a question
response = ask_system("What's the system health?")
print(response)

# With conversation context
conversation_id = "session-123"
response = ask_system("And why is CPU high?", conversation_id=conversation_id)
```

## Configuration

Edit `/opt/mythos/llm_diagnostics/config/diagnostics_config.yaml`:

```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "llama3.2:3b"
  temperature: 0.1  # Low for consistent diagnostics
  
mcp_server:
  host: "localhost"
  port: 8765
  
logging:
  log_conversations: true
  log_tool_calls: true
  
neo4j:
  # Uses environment variables from ~/.config/arcturus/systemd.env
```

## Available Tools (for LLM)

The LLM has access to these diagnostic functions:

1. **get_system_health()**: Current system status, health score, recent issues
2. **trace_failure(service_name)**: Root cause analysis for service failures
3. **get_recent_events(minutes, event_types)**: Query recent events by type/time
4. **get_service_status(service_name)**: Detailed service state
5. **get_high_resource_processes()**: Processes using high CPU/memory
6. **predict_failure(service_name)**: Predictive failure analysis

## Example Interactions

### Health Check
```
You: How is the system?

LLM: System health score is 100. All services are running normally. 
     5 active processes monitored, no recent issues detected.
```

### Failure Diagnosis
```
You: Why did the neo4j backup fail?

LLM: The backup failed due to low disk space (95% full). 
     Root cause: /var/log accumulated 20GB of old logs. 
     Recommendation: Clear logs older than 30 days.
```

### Resource Investigation
```
You: What's using memory?

LLM: Top processes:
     - java (Neo4j): 1.2GB
     - firefox: 888MB
     - gnome-shell: 930MB
     All within normal ranges.
```

## Architecture

```
User Question
    ↓
mythos-ask CLI / Python API
    ↓
Ollama (Local LLM)
    ↓
MCP Server (Tool Provider)
    ↓
Diagnostics Interface (diagnostics.py)
    ↓
Neo4j Graph (System State)
    ↓
Response + Conversation Logging
```

## Performance

- **First query**: ~2-3 seconds (model loading)
- **Subsequent queries**: ~500ms-1s (depending on complexity)
- **Memory usage**: ~2-4GB (for llama3.2:3b)
- **CPU usage**: Minimal when idle, spikes during queries

## Verification

```bash
# Check MCP server is running
systemctl --user status mythos-mcp-server

# Check Ollama is running
systemctl --user status ollama

# Test a query
mythos-ask "system health"

# View conversation logs
cypher-shell "MATCH (c:Conversation) RETURN c ORDER BY c.timestamp DESC LIMIT 5"
```

## Troubleshooting

### Ollama Not Found
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2:3b
```

### MCP Server Not Starting
```bash
# Check logs
journalctl --user -u mythos-mcp-server -n 50

# Check Python dependencies
pip list | grep -E "(anthropic|ollama)"
```

### Connection Issues
```bash
# Test MCP server directly
curl http://localhost:8765/health

# Test Ollama
curl http://localhost:11434/api/tags
```

## Rollback

```bash
# Stop services
systemctl --user stop mythos-mcp-server
systemctl --user disable mythos-mcp-server

# Remove installation
sudo rm -rf /opt/mythos/llm_diagnostics

# Or use rollback script
./rollback.sh

# Or use pa command
pa-rollback 6
```

## Next Steps

After this patch:
- **Patch 0007**: Self-healing capabilities (LLM can generate and execute fixes)
- **Patch 0008**: Pattern learning (system learns from diagnostics over time)
- **Patch 0009**: Predictive maintenance (prevent failures before they happen)

## Security Notes

- MCP server only listens on localhost (not exposed to network)
- LLM has read-only access to graph (cannot modify system)
- All conversations logged for audit trail
- No external API calls (fully local/sovereign)

---

**Ready to install?** Run `./install.sh` to integrate LLM diagnostics with your monitoring system!
