# Mythos Command Center — Design System

## Overview

The Command Center uses React + Vite, served at `/app/v2` via FastAPI.
All styling is inline (no Tailwind, no CSS modules). Theme constants live in `styles/theme.js`.

---

## Theme

```js
import { T, mono, serif, fmt, fmtShort } from '../styles/theme'
```

| Token | Use |
|-------|-----|
| `T.bg` | Page background `#0a0e17` |
| `T.bgCard` | Card/panel background `#111827` |
| `T.bgHover` | Row/item hover `#1a2332` |
| `T.border` | Standard border `#1e293b` |
| `T.text` | Primary text `#e2e8f0` |
| `T.textDim` | Secondary text `#64748b` |
| `T.textMuted` | Tertiary/label text `#475569` |
| `T.cyan` | Primary accent (active states, links) |
| `T.gold` | Brand accent (MYTHOS wordmark, special items) |
| `T.green/red/amber/blue/purple` | Semantic colors + matching `Bg` variants |

**Fonts:**
- `serif` → Cinzel (headings, section titles, brand)
- `mono` → JetBrains Mono (data, values, code, labels)
- Default (DM Sans) → body text, descriptions

**Currency:** `fmt(n)` → `$1,234.56`, `fmtShort(n)` → `$1.2k`

---

## Breakpoints

```js
import { useMobile, useTablet, useDesktop } from '../hooks/useMediaQuery'
```

| Hook | Max Width | Use |
|------|-----------|-----|
| `useMobile()` | 480px | Phone layout |
| `useTablet()` | 768px | Tablet + hamburger trigger |
| `useDesktop()` | 1024px | Compact desktop |

At tablet (≤768px): top nav collapses to hamburger, sidebar becomes drawer overlay.

---

## UI Components

All importable from `components/ui`:

```js
import { PageHeader, Grid, Button, DataTable, EmptyState } from '../components/ui'
```

### PageHeader
Standard page title block with optional icon and action buttons.
```jsx
<PageHeader title="Overview" subtitle="Financial snapshot" icon="◈" color={T.cyan}
  actions={<Button variant="primary" size="sm">Export</Button>} />
```

### Grid
Responsive auto-fill grid. Uses CSS `minmax()` for automatic column wrapping.
```jsx
<Grid min={260} gap={16}>{cards}</Grid>    // auto-fill
<Grid cols={3} gap={16}>{cards}</Grid>     // fixed columns
```

### Button
Styled button with variants.
```jsx
<Button variant="primary">Save</Button>   // cyan
<Button variant="ghost">Cancel</Button>    // transparent
<Button variant="danger" size="sm">Delete</Button>
<Button variant="gold">Special</Button>
```

### Card + StatCard
Already exist in `components/`. Card wraps content with themed border/bg.
StatCard shows a labeled metric value.
```jsx
<Card highlight="success">content</Card>
<StatCard label="Safe to Spend" value={fmt(420)} color={T.green} />
```

### DataTable
Responsive table — renders as standard table on desktop, stacks to cards on mobile.
```jsx
<DataTable
  columns={[
    { key: 'date', label: 'Date', width: 100 },
    { key: 'amount', label: 'Amount', align: 'right', render: (v) => fmt(v) },
  ]}
  rows={data}
  onRowClick={(row) => handleClick(row)}
  emptyText="No transactions"
/>
```

### EmptyState
Centered placeholder for empty or coming-soon states.
```jsx
<EmptyState icon="◎" title="No Records" message="Import data to get started"
  action={<Button variant="primary">Import</Button>} />
```

---

## Layout Architecture

### Adding a New Section

1. **Create page components** in `pages/{section}/`
2. **Add routes** in `App.jsx` under the `<CommandCenter>` layout
3. **Add sidebar config** (optional) in `CommandCenter.jsx` → `sidebarConfigs`
4. **Update Home.jsx** section card if needed

### Sidebar Config Pattern

```js
// In CommandCenter.jsx → sidebarConfigs
people: [
  {
    label: "Genealogy",
    items: [
      { icon: "🌳", label: "Family Tree", to: "/people/tree" },
      { icon: "👤", label: "Individuals", to: "/people/list" },
    ]
  }
]
```

The sidebar only renders when the current URL section has a matching config.
Account strip only shows in Finance.

### Page Template

Standard page structure:

```jsx
import { T, mono, fmt } from '../../styles/theme'
import { PageHeader, Grid, Button, DataTable } from '../../components/ui'
import { useApi } from '../../hooks/useApi'
import { useMobile } from '../../hooks/useMediaQuery'

export default function MyPage() {
  const isMobile = useMobile()
  const { data, loading, error } = useApi('/api/my-endpoint')

  if (loading) return <div style={{ color: T.textMuted, padding: 32, ...mono }}>Loading...</div>

  return (
    <div>
      <PageHeader title="Page Name" subtitle="Description" icon="◈" />
      <Grid min={260}>
        {/* content */}
      </Grid>
    </div>
  )
}
```

---

## Data Hooks

### useApi
```js
const { data, loading, error, refetch } = useApi('/api/endpoint?param=value')
```
Auto-fetches on mount and when URL changes. Use `{ skip: true }` to defer.

### useAccount
```js
const { account, setAccount } = useAccount()  // 'combined' | 'usaa' | 'sun'
```
Global context from AccountProvider. Append `?account=${account}` to API URLs for filtering.

---

## Conventions

- **Inline styles only** — no CSS modules, no Tailwind
- **Theme tokens** — always use `T.*` constants, never hardcode colors
- **Font stacks** — spread `...mono` or `...serif` into style objects
- **Spacing** — 4/8/12/16/24/32/48px scale
- **Border radius** — 6px (buttons), 8px (cards/mobile), 10px (large cards)
- **Transitions** — `0.15s` for micro, `0.2s` for layout, `0.25s` for drawer
- **Labels** — 10px uppercase, letterSpacing 1-1.2px, `T.textMuted`
- **Data values** — `mono`, bold, `T.text` or semantic color
