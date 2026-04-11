---
title: "Command Center v2 Development Guide"
category: reference
status: active
stream: SYS
location: docs
tags: [frontend, react, development]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Command Center v2 — Development Guide
> **Location:** `/opt/mythos/docs/COMMAND_CENTER_DEV_GUIDE.md`
> **Last Updated:** 2026-02-25 (Patch 0143)
> **Status:** Authoritative reference for all Command Center frontend work

---

## Why React (Design Decision Record)

We evaluated React, HTMX+Jinja2, Svelte, and Vue for the Command Center. React was chosen for these specific reasons:

1. **Client-side state complexity.** The Command Center needs features like what-if expense modeling, interactive chart filtering, drag-and-drop, and inline editing. These require real client-side state management. HTMX shifts logic to the server, which works for CRUD apps but creates friction for interactive dashboards.

2. **Charting ecosystem.** Recharts (React-native) is the richest charting library for this use case. Chart.js via CDN (HTMX path) lacks composability — you can't embed custom tooltips, gradient fills, or reference lines as declaratively.

3. **Component reuse.** Shared components (Card, StatCard, ChartTooltip, SelectorBtn) compound across pages. Every new page gets the theme, formatting, and interaction patterns for free.

4. **AI buildability.** React components are the most well-understood pattern for LLM code generation (including Iris's future builder mode). JSX is self-documenting. An LLM can generate a complete new page by following the patterns in this doc.

5. **Already invested.** Vite + React is installed on Arcturus, the build pipeline works, and three pages are live. Switching frameworks mid-build creates debt for zero gain.

**What React is NOT used for:** The old dashboard (`/app/finance/`) remains vanilla HTML/JS served by Jinja2 templates. Telegram commands remain server-side. The API remains FastAPI/Python. React is ONLY for the Command Center v2 SPA at `/app/v2/*`.

---

## Architecture Overview

```
Browser → https://mythos-api.denkers.co/app/v2/*
         ↓
    FastAPI (frontend.py) serves React dist/index.html
         ↓
    React Router (BrowserRouter, basename="/app/v2")
         ↓
    CommandCenter layout (topbar + sidebar + <Outlet />)
         ↓
    Page component (e.g., Forecast.jsx)
         ↓
    useApi() hook → fetch("/api/finance/forecast?days=30")
         ↓
    FastAPI API route → PostgreSQL → JSON response
```

### Key Directories

```
/opt/mythos/web/frontend/           ← Vite + React project root
├── src/
│   ├── main.jsx                    ← Entry: BrowserRouter basename="/app/v2"
│   ├── App.jsx                     ← All routes defined here
│   ├── layouts/
│   │   └── CommandCenter.jsx       ← Shell: topbar, collapsible sidebar, <Outlet />
│   ├── pages/
│   │   ├── Placeholder.jsx         ← "Coming soon" stub for unbuilt routes
│   │   └── finance/
│   │       ├── Overview.jsx        ← Landing dashboard
│   │       ├── Spending.jsx        ← Spending analytics (3 sub-views)
│   │       └── Forecast.jsx        ← Balance projection + what-if modeling
│   ├── components/
│   │   ├── Card.jsx                ← Base card, supports highlight="red|amber|green|blue"
│   │   ├── StatCard.jsx            ← Label/value/sub display card
│   │   └── ChartTooltip.jsx        ← Recharts custom tooltip base
│   ├── hooks/
│   │   └── useApi.js               ← Fetch wrapper: { data, loading, error, refetch }
│   └── styles/
│       ├── theme.js                ← T colors, mono/serif fonts, fmt/fmtShort formatters
│       └── global.css              ← CSS reset, scrollbar styling, font imports
├── dist/                           ← Built output (served by FastAPI, git-ignored)
├── index.html                      ← Vite entry HTML
├── package.json                    ← react@18, react-router-dom@6, recharts@2, vite@5
└── vite.config.js                  ← base: '/app/v2/'

/opt/mythos/api/routes/
├── frontend.py                     ← Serves /app/v2/* (React SPA fallback)
├── overview.py                     ← /api/finance/overview
├── spending_analytics.py           ← /api/finance/spending/analytics
└── finance.py                      ← All other /api/finance/* endpoints
```

---

## Design System

### Theme Object (`styles/theme.js`)

ALL colors, fonts, and formatters live in theme.js. Never hardcode colors.

```javascript
import { T, mono, serif, fmt, fmtShort } from '../../styles/theme'
```

| Token        | Value             | Use                          |
|-------------|-------------------|------------------------------|
| `T.bg`       | `#0a0e17`         | Page background              |
| `T.bgCard`   | `#111827`         | Card/panel background        |
| `T.bgHover`  | `#1a2332`         | Hover states                 |
| `T.border`   | `#1e293b`         | Borders, dividers            |
| `T.text`     | `#e2e8f0`         | Primary text                 |
| `T.textDim`  | `#64748b`         | Secondary/label text         |
| `T.textMuted`| `#475569`         | Tertiary/disabled text       |
| `T.green`    | `#22c55e`         | Positive values, income      |
| `T.red`      | `#ef4444`         | Negative values, bills, danger |
| `T.amber`    | `#f59e0b`         | Warnings, what-if overlays   |
| `T.blue`     | `#3b82f6`         | Active selections, CTAs      |
| `T.cyan`     | `#06b6d4`         | Charts primary line          |
| `T.purple`   | `#a855f7`         | Accent, secondary charts     |
| `T.gold`     | `#d4a574`         | Mythos brand accent          |
| `*Bg` variants | `rgba(color,0.08)` | Tinted backgrounds        |

### Fonts

| Object  | Value                          | Use              |
|---------|--------------------------------|------------------|
| `mono`  | `{ fontFamily: "'JetBrains Mono', monospace" }` | Data, numbers, labels, code |
| `serif` | `{ fontFamily: "'Cinzel', serif" }`              | Page titles, headings       |

Apply via spread: `style={{ fontSize: 13, color: T.textDim, ...mono }}`

### Formatters

| Function    | Example Input | Output       | Use                        |
|------------|--------------|--------------|----------------------------|
| `fmt(n)`   | `1234.56`    | `$1,234.56`  | Full currency display      |
| `fmt(-50)` | `-50`        | `-$50.00`    | Negative values            |
| `fmt(null)`| `null`       | `—`          | Missing data               |
| `fmtShort(n)` | `1234`   | `$1.2k`      | Chart axis ticks, compact  |

### Styling Rules

1. **Inline styles only.** No CSS modules, no Tailwind, no styled-components. Every style is a JS object.
2. **Spread theme tokens.** Never write `fontFamily: 'JetBrains Mono'` — always `...mono`.
3. **Use T.* for all colors.** Never hardcode hex values outside theme.js.
4. **Consistent border-radius:** 6px for inputs/buttons, 10px for cards, 8px for tooltips.
5. **Consistent spacing:** 8/12/16/20/24px. Prefer `gap` in flex/grid over margins.
6. **No localStorage, no sessionStorage.** All state is API-driven or React state.

---

## Component Patterns

### Page Component Template

Every page follows this exact structure:

```jsx
import { useState, useMemo } from 'react'
import { useApi } from '../../hooks/useApi'
import { T, mono, serif, fmt, fmtShort } from '../../styles/theme'
import Card from '../../components/Card'
// import Recharts components as needed

export default function MyPage() {
  // 1. Local UI state (selectors, filters, toggles)
  const [filter, setFilter] = useState('default')

  // 2. API call (one per page where possible)
  const { data, loading, error, refetch } = useApi(`/api/some/endpoint?filter=${filter}`)

  // 3. Derived/computed data (useMemo for expensive transforms)
  const processedData = useMemo(() => {
    if (!data) return []
    return data.items.map(/* transform */)
  }, [data])

  // 4. Loading state
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: 400, color: T.textDim, ...mono }}>
        Loading…
      </div>
    )
  }

  // 5. Error state
  if (error) {
    return (
      <Card highlight="red">
        <div style={{ color: T.red, ...mono }}>Error: {error}</div>
      </Card>
    )
  }

  // 6. Render
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header: title + selectors */}
      {/* Alert banners (conditional) */}
      {/* Stat pills row */}
      {/* Main content (charts, tables, etc.) */}
    </div>
  )
}
```

### Shared Components

**Card** — Base container. Use for every content section.
```jsx
<Card>content</Card>
<Card highlight="red">danger content</Card>
<Card highlight="amber">warning content</Card>
```

**StatCard** — Metric display. Label + value + optional sub-text.
```jsx
<StatCard label="Total Spending" value={fmt(2340)} sub="This month" />
```

**useApi(url, options)** — Data fetching hook.
```jsx
const { data, loading, error, refetch } = useApi('/api/finance/overview')
const { data } = useApi('/api/some/endpoint', { skip: !ready }) // conditional fetch
```
Returns `{ data, loading, error, refetch }`. Automatically fetches on mount and when URL changes.

### Selector Button Pattern

For account/period/view toggles:

```jsx
const SelectorBtn = ({ active, onClick, children }) => (
  <button onClick={onClick} style={{
    background: active ? T.blue : 'transparent',
    color: active ? '#fff' : T.textDim,
    border: `1px solid ${active ? T.blue : T.border}`,
    borderRadius: 6, padding: '6px 14px', fontSize: 12,
    cursor: 'pointer', ...mono,
  }}>
    {children}
  </button>
)
```

### Section Header Pattern

Uppercase, letterspaced, mono:
```jsx
<div style={{ fontSize: 13, color: T.textDim, textTransform: 'uppercase',
  letterSpacing: 1.5, marginBottom: 12, ...mono }}>
  Section Title
</div>
```

### Page Title Pattern

Cinzel serif, no bold:
```jsx
<h2 style={{ margin: 0, fontSize: 20, color: T.text, ...serif, fontWeight: 400 }}>
  Page Title
</h2>
```

---

## Recharts Patterns

All charts use Recharts v2. Import from `'recharts'`.

### Standard Chart Setup

```jsx
<Card>
  <div style={{ width: '100%', height: 380 }}>
    <ResponsiveContainer>
      <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={T.border} opacity={0.5} />
        <XAxis dataKey="label" tick={{ fill: T.textDim, fontSize: 11, ...mono }}
          axisLine={{ stroke: T.border }} tickLine={{ stroke: T.border }} />
        <YAxis tickFormatter={fmtShort} tick={{ fill: T.textDim, fontSize: 11, ...mono }}
          axisLine={{ stroke: T.border }} tickLine={{ stroke: T.border }} width={60} />
        <Tooltip content={<CustomTooltip />} />
        {/* Areas, Bars, Lines, ReferenceLines, etc. */}
      </ComposedChart>
    </ResponsiveContainer>
  </div>
</Card>
```

### Chart Color Assignments

| Purpose          | Color     | Gradient  |
|-----------------|-----------|-----------|
| Primary data    | `T.cyan`  | green→transparent |
| Secondary/alt   | `T.purple`| purple→transparent |
| Positive values | `T.green` | — |
| Negative values | `T.red`   | red→transparent |
| What-if overlay | `T.amber` | amber→transparent, dashed stroke |
| Reference lines | `T.red` (danger), `T.green` (income) | dashed |

### Custom Tooltip Pattern

```jsx
function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div style={{
      background: T.bgCard, border: `1px solid ${T.border}`,
      borderRadius: 8, padding: '12px 16px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.4)', minWidth: 200,
    }}>
      {/* Tooltip content */}
    </div>
  )
}
```

---

## API Integration Patterns

### One API Call Per Page

Each page should ideally make ONE API call that returns everything it needs. This reduces loading states and simplifies the component. See `/api/finance/overview` as the gold standard — it returns balances, bills due, forecast alerts, spending, and transactions in one response.

### API Route Pattern

```python
# /opt/mythos/api/routes/my_endpoint.py
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
import json, os, psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

router = APIRouter(prefix="/api/mymodule", tags=["mymodule"])

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal): return float(o)
        if isinstance(o, (date, datetime)): return o.isoformat()
        return super().default(o)

def json_response(data):
    return JSONResponse(content=json.loads(json.dumps(data, cls=DecimalEncoder)))

def get_db():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )

@router.get("/my-data")
async def get_my_data(request: Request):
    conn = get_db(); cur = conn.cursor()
    # ... queries ...
    conn.close()
    return json_response({...})
```

### Registering a New Route in main.py

Add import at the top:
```python
from api.routes.my_endpoint import router as my_endpoint_router
```

Add include near the other router includes:
```python
app.include_router(my_endpoint_router)
```

---

## Adding a New Page — Full Checklist

### Step 1: Create API endpoint (if needed)

- File: `/opt/mythos/api/routes/my_endpoint.py`
- Follow the API Route Pattern above
- Return all data the page needs in one call
- Register in `main.py`

### Step 2: Create React component

- File: `/opt/mythos/web/frontend/src/pages/{section}/MyPage.jsx`
- Follow the Page Component Template above
- Import from theme, hooks, and components

### Step 3: Add route to App.jsx

```jsx
import MyPage from './pages/section/MyPage'
// ...inside <Routes>:
<Route path="/section/mypage" element={<MyPage />} />
```

### Step 4: Add sidebar link (if applicable)

Edit `CommandCenter.jsx` to add the nav item. Sidebar links follow this structure:
```jsx
{ path: '/finance/mypage', label: 'My Page', icon: '📊' }
```

### Step 5: Build and deploy

Via patch `install.sh`:
```bash
cd /opt/mythos/web/frontend && npx vite build
sudo systemctl restart mythos-api.service
```

### Step 6: Update documentation

- Add to this file's Architecture section
- Update ARCHITECTURE.md if it's a stable feature
- Update TODO.md to mark work complete

---

## Patch Template for Frontend Work

```bash
mkdir -p /home/claude/patch_NNNN_description/opt/mythos/{api/routes,web/frontend/src/pages/finance,docs}

# Required files:
# 1. manifest.json
# 2. install.sh
# 3. New React component(s)
# 4. Updated App.jsx (with new route)
# 5. New API route (if needed)
# 6. Updated COMMAND_CENTER_DEV_GUIDE.md (if patterns change)
```

### install.sh Template for Frontend Patches

```bash
#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Patch NNNN: Description ==="

# Copy API route (if new)
# echo "→ Copying my_endpoint.py..."
# sudo cp "$PATCH_DIR/opt/mythos/api/routes/my_endpoint.py" /opt/mythos/api/routes/my_endpoint.py

# Copy React components
echo "→ Copying React components..."
sudo cp "$PATCH_DIR/opt/mythos/web/frontend/src/pages/finance/MyPage.jsx" \
  /opt/mythos/web/frontend/src/pages/finance/MyPage.jsx

# Copy updated App.jsx
echo "→ Copying App.jsx..."
sudo cp "$PATCH_DIR/opt/mythos/web/frontend/src/App.jsx" \
  /opt/mythos/web/frontend/src/App.jsx

# Copy docs
echo "→ Updating documentation..."
sudo cp "$PATCH_DIR/opt/mythos/docs/COMMAND_CENTER_DEV_GUIDE.md" \
  /opt/mythos/docs/COMMAND_CENTER_DEV_GUIDE.md

# Register new API route in main.py (if new endpoint)
# Use sed or python string replacement — follow patch standard v2

# Fix ownership
sudo chown -R adge:adge /opt/mythos/web/frontend/src/
sudo chown -R adge:adge /opt/mythos/docs/

# Build frontend
echo "→ Building frontend..."
cd /opt/mythos/web/frontend
npx vite build

# Restart API
echo "→ Restarting API..."
sudo systemctl restart mythos-api.service
sleep 2

if sudo systemctl is-active --quiet mythos-api.service; then
  echo "✅ Patch NNNN deployed"
else
  echo "❌ API failed to start!"
  sudo journalctl -u mythos-api.service -n 20 --no-pager
  exit 1
fi
```

---

## Available Libraries (package.json)

| Package | Version | Use |
|---------|---------|-----|
| `react` | 18.x | UI framework |
| `react-dom` | 18.x | DOM rendering |
| `react-router-dom` | 6.x | Client-side routing |
| `recharts` | 2.x | All charts (Area, Bar, Pie, Line, Composed) |
| `vite` | 5.x | Build tool, dev server |

No other dependencies. If a new library is needed, add it via `npm install` in the patch install.sh and document here.

---

## Pages Inventory

| Route | Component | API Endpoint | Status |
|-------|-----------|-------------|--------|
| `/finance/overview` | `Overview.jsx` | `/api/finance/overview` | ✅ Live |
| `/finance/spending` | `Spending.jsx` | `/api/finance/spending/analytics` | ✅ Live |
| `/finance/forecast` | `Forecast.jsx` | `/api/finance/forecast` | ✅ Live (0143) |
| `/finance/transactions` | `Placeholder` | `/api/finance/transactions` | 📋 Next |
| `/finance/bills` | `Placeholder` | `/api/finance/bills/tracker` | 📋 Queued |
| `/finance/categories` | `Placeholder` | `/api/finance/categories` | 📋 Queued |
| `/finance/accounts` | `Placeholder` | `/api/finance/accounts` | 📋 Queued |

---

## Anti-Patterns (What NOT to Do)

1. **Don't use Tailwind classes.** We use inline styles with theme tokens. Tailwind would require a compiler setup we don't have.
2. **Don't use CSS modules or external stylesheets** (except global.css). Keep styles colocated.
3. **Don't use localStorage/sessionStorage.** State comes from the API or React state.
4. **Don't make multiple API calls per page** unless absolutely necessary. Prefer a single aggregated endpoint.
5. **Don't hardcode colors or font families.** Always use `T.*`, `mono`, `serif`.
6. **Don't create separate CSS/JS files for a page.** Each page is ONE .jsx file with everything inline.
7. **Don't modify the old dashboard** (`/app/finance/`). It will be retired after all pages migrate.
8. **Don't install npm packages without documenting them** in this guide and package.json.

---

## Future Sections (Will Be Built)

When these areas get Command Center pages, they follow the same patterns:

- **Iris Chat** — `/iris/chat` — Would need WebSocket integration (new pattern to document)
- **Calendar** — `/calendar` — Standard page pattern, new API endpoint
- **Routines** — `/routines` — Standard page pattern
- **System** — `/system` — Service status, model management
- **Consciousness** — `/consciousness` — Grid visualization, perception log

Each new domain gets its own subdirectory under `pages/` and its own API route file.

---

*This document is the single source of truth for Command Center development.*
*Every AI session, every Iris builder task, every future patch — starts here.*
