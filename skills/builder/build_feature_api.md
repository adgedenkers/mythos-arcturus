---
name: build_feature_api
version: "1.0"
category: builder
risk_tier: T2-patch
description: >
  Design and deploy a new FastAPI endpoint or service within the Mythos gateway
  architecture. Use when Ka'tuar'el requests a new API route, webhook handler,
  data service, or any HTTP-accessible functionality. Triggers on: "new API",
  "add an endpoint", "FastAPI route", "build a service", or when another skill
  needs an API component.
requires:
  services: [mythos-gateway, postgresql]
  tools: [python3, bash]
  files:
    - /opt/mythos/docs/ARCHITECTURE.md
    - /opt/mythos/gateway/  # current API structure
  env_vars: []
inputs:
  required:
    - what the endpoint does (functionality description)
    - HTTP method and route path
  optional:
    - request/response schema
    - authentication requirements
    - related database tables
outputs:
  files:
    - patch via build_patch skill
  formats: [.zip]
  destinations:
    - deployed via patch system
---

# Build Feature: API Endpoint

## Purpose

Extend the Mythos FastAPI gateway with new endpoints. All API features follow
the same pattern: route definition, request validation, business logic,
response formatting, and error handling.

## Pre-Flight Checks

1. **Get current API structure:**
   ```bash
   D=~/diag.txt; > "$D"
   echo "=== GATEWAY STRUCTURE ===" >> "$D"
   find /opt/mythos/gateway -name "*.py" | head -30 >> "$D" 2>&1
   echo -e "\n\n=== EXISTING ROUTES ===" >> "$D"
   grep -rn "@app\.\|@router\." /opt/mythos/gateway/ >> "$D" 2>&1
   echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
   cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
   cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
   ```

2. **Check for route conflicts** — ensure the proposed path doesn't collide
   with existing routes.

3. **Identify database dependencies** — if the endpoint reads/writes data,
   verify the tables exist or plan a migration.

## Process

### Step 1: Design the Endpoint

Define:
- **Route:** `METHOD /path/{params}`
- **Request body:** Pydantic model (if POST/PUT)
- **Query params:** Optional filters
- **Response model:** What gets returned
- **Auth:** Required or public?
- **Error cases:** What can go wrong and what status codes to return

Present design to Ka'tuar'el for confirmation.

### Step 2: Implement

Write the route handler following Mythos patterns:
- Use Pydantic models for request/response validation
- Use dependency injection for database connections
- Include proper error handling with HTTPException
- Add logging for debugging
- Follow existing code style in the gateway directory

### Step 3: Add Database Migration (if needed)

If new tables or columns are required:
- Write SQL migration file
- Include in patch install.sh
- Run migration before deploying code

### Step 4: Deploy via build_patch

Package everything as a numbered patch using the build_patch skill.
Include the route file, any model files, updated __init__.py or router
registration, and migration SQL.

### Step 5: Test

After deployment, verify:
- `curl` the endpoint and confirm expected response
- Test error cases
- Check logs: `journalctl -u mythos-gateway -n 20`

## Output Format

Standard Mythos patch (see build_patch skill).

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Route 404 after deploy | Router not registered | Check __init__.py or app.include_router() |
| 500 on request | Code error in handler | Check journalctl, fix and redeploy |
| Pydantic validation error | Wrong request format | Verify model matches expected input |
| Database error | Missing table or wrong query | Check migration ran, verify SQL |

---

_Last updated: 2026-02-22_
_Author: Ka'tuar'el_
