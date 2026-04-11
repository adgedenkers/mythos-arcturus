import { useState, useEffect } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { T, mono, serif } from '../styles/theme'
import { AccountProvider, useAccount, accountLabel } from '../hooks/useAccount.jsx'
import { useTablet, useMobile } from '../hooks/useMediaQuery'
// ── Top-level sections ────────────────────────────────────
const topNavItems = [
  { label: "Home",     to: "/" },
  { label: "Finance",  to: "/finance" },
  { label: "People",   to: "/people" },
  { label: "Rolodex",  to: "/rolodex" },
  { label: "Iris",     to: "/iris" },
  { label: "SDIP",     to: "/sdip" },
  { label: "Transits", to: "/transits" },
  { label: "Research", to: "/research" },
  { label: "Registry", to: "/registry" },
  { label: "Sessions", to: "/sessions" },
  { label: "System",   to: "/system" },
]
// ── Sidebar configs per section ───────────────────────────
const sidebarConfigs = {
  finance: [
    {
      label: "Dashboard",
      items: [
        { icon: "⬡", label: "Dashboard",    to: "/finance/dashboard" },
        { icon: "📋", label: "Bills Detail", to: "/finance/bills-detail" },
      ]
    },
    {
      label: "Finance",
      items: [
        { icon: "◈", label: "Overview",     to: "/finance/overview" },
        { icon: "📊", label: "Spending",     to: "/finance/spending" },
        { icon: "⇄", label: "Transactions", to: "/finance/transactions" },
        { icon: "📅", label: "Bills",        to: "/finance/bills" },
        { icon: "🗺", label: "Bills Map",    to: "/finance/bills-map" },
        { icon: "⟁", label: "Matcher",     to: "/finance/pattern-matcher" },
        { icon: "📈", label: "Forecast",     to: "/finance/forecast" },
        { icon: "🗓", label: "Calendar",     to: "/finance/calendar" },
        { icon: "📆", label: "Projection",   to: "/finance/projection" },
      ]
    },
    {
      label: "Manage",
      items: [
        { icon: "🏷", label: "Categories",  to: "/finance/categories" },
        { icon: "🏦", label: "Accounts",    to: "/finance/accounts" },
      ]
    }
  ],
  people: [
    {
      label: "People",
      items: [
        { icon: "⟡", label: "Browse", to: "/people/list" },
      ]
    }
  ],
  rolodex: [
    {
      label: "Rolodex",
      items: [
        { icon: "◈", label: "Browse",     to: "/rolodex/browse" },
      ]
    },
    {
      label: "Legacy",
      items: [
        { icon: "📋", label: "People (v1)", to: "/people/list" },
      ]
    }
  ],
  transits: [
    {
      label: "Transit Pressure",
      items: [
        { icon: "☉", label: "Ka'tuar'el",  to: "/transits/kataurel" },
        { icon: "☽", label: "Seraphe",     to: "/transits/seraphe" },
      ]
    }
  ],
}
function getSection(pathname) {
  const seg = pathname.split('/').filter(Boolean)[0]
  return seg || 'home'
}
// ── Hamburger Icon ────────────────────────────────────────
function HamburgerIcon({ open, onClick }) {
  const bar = {
    display: 'block',
    width: 20,
    height: 2,
    background: T.textDim,
    borderRadius: 1,
    transition: 'all 0.25s ease',
  }
  return (
    <button
      onClick={onClick}
      aria-label="Toggle menu"
      style={{
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        padding: 8,
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <span style={{
        ...bar,
        transform: open ? 'rotate(45deg) translate(3px, 3px)' : 'none',
      }} />
      <span style={{
        ...bar,
        opacity: open ? 0 : 1,
      }} />
      <span style={{
        ...bar,
        transform: open ? 'rotate(-45deg) translate(3px, -3px)' : 'none',
      }} />
    </button>
  )
}
// ── Account Strip ─────────────────────────────────────────
function AccountStrip() {
  const { account, setAccount } = useAccount()
  const isMobile = useMobile()
  const chipStyle = (active) => ({
    padding: isMobile ? '6px 10px' : '4px 12px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 500,
    cursor: 'pointer',
    border: `1px solid ${active ? T.cyan : T.border}`,
    background: active ? `${T.cyan}18` : 'transparent',
    color: active ? T.cyan : T.textMuted,
    transition: 'all 0.15s',
    ...mono,
    flex: isMobile ? 1 : 'none',
    textAlign: 'center',
  })
  const dotColor = account === 'combined' ? T.cyan
    : account === 'usaa' ? '#3b82f6'
    : '#22c55e'
  return (
    <div style={{
      display: 'flex',
      alignItems: isMobile ? 'stretch' : 'center',
      justifyContent: 'space-between',
      flexDirection: isMobile ? 'column' : 'row',
      padding: isMobile ? '8px 16px' : '6px 24px',
      gap: isMobile ? 8 : 0,
      background: T.bg,
      borderBottom: `1px solid ${T.border}`,
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{
          width: 6, height: 6, borderRadius: '50%',
          background: dotColor,
          boxShadow: `0 0 6px ${dotColor}66`,
        }} />
        <span style={{ fontSize: 11, color: T.textDim, ...mono }}>
          Viewing: <span style={{ color: T.text }}>{accountLabel(account)}</span>
        </span>
      </div>
      <div style={{ display: 'flex', gap: 4 }}>
        <button onClick={() => setAccount('combined')} style={chipStyle(account === 'combined')}>
          Combined
        </button>
        <button onClick={() => setAccount('usaa')} style={chipStyle(account === 'usaa')}>
          USAA
        </button>
        <button onClick={() => setAccount('sun')} style={chipStyle(account === 'sun')}>
          SUN
        </button>
      </div>
    </div>
  )
}
// ── Mobile Drawer (overlay) ───────────────────────────────
function MobileDrawer({ open, onClose, section, sidebar, location }) {
  if (!open) return null
  const linkStyle = (active) => ({
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '12px 20px',
    fontSize: 15,
    fontWeight: 500,
    color: active ? T.cyan : T.textDim,
    background: active ? `${T.cyan}12` : 'transparent',
    textDecoration: 'none',
    borderBottom: `1px solid ${T.border}`,
  })
  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.6)',
          zIndex: 99,
        }}
      />
      {/* Drawer */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        width: 280,
        background: T.bgCard,
        zIndex: 100,
        overflowY: 'auto',
        boxShadow: '4px 0 24px rgba(0,0,0,0.5)',
      }}>
        {/* Drawer header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: `1px solid ${T.border}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <span style={{ ...serif, fontSize: 16, fontWeight: 600, letterSpacing: 4, color: T.gold }}>
            MYTHOS
          </span>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none', color: T.textDim,
              fontSize: 20, cursor: 'pointer', padding: 4,
            }}
          >✕</button>
        </div>
        {/* Section nav */}
        <div style={{ padding: '8px 0' }}>
          <div style={{
            fontSize: 10, textTransform: 'uppercase', letterSpacing: 1.2,
            color: T.textMuted, padding: '12px 20px 4px',
          }}>Sections</div>
          {topNavItems.map((n) => {
            const isHome = n.to === '/'
            const active = isHome
              ? (section === 'home' || location.pathname === '/')
              : location.pathname.startsWith(n.to)
            return (
              <NavLink
                key={n.label}
                to={n.to}
                onClick={onClose}
                style={linkStyle(active)}
              >
                {n.label}
              </NavLink>
            )
          })}
        </div>
        {/* Sub-nav for current section */}
        {sidebar && (
          <div style={{ padding: '8px 0', borderTop: `1px solid ${T.border}` }}>
            {sidebar.map((group) => (
              <div key={group.label}>
                <div style={{
                  fontSize: 10, textTransform: 'uppercase', letterSpacing: 1.2,
                  color: T.textMuted, padding: '12px 20px 4px',
                }}>{group.label}</div>
                {group.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={onClose}
                    style={({ isActive }) => linkStyle(isActive)}
                  >
                    <span style={{ fontSize: 16, width: 22, textAlign: 'center' }}>{item.icon}</span>
                    {item.label}
                  </NavLink>
                ))}
              </div>
            ))}
          </div>
        )}
        {/* Logout */}
        <div style={{ padding: '16px 20px', borderTop: `1px solid ${T.border}` }}>
          <a href="/auth/logout" style={{
            ...mono, fontSize: 12, color: T.textMuted, textDecoration: 'none',
          }}>logout</a>
        </div>
      </div>
    </>
  )
}
// ── Layout ────────────────────────────────────────────────
function CommandCenterInner() {
  const location = useLocation()
  const isTablet = useTablet()
  const section = getSection(location.pathname)
  const sidebar = sidebarConfigs[section] || null
  const showAccountStrip = section === 'finance' && location.pathname !== '/finance/dashboard'
  const [drawerOpen, setDrawerOpen] = useState(false)
  // Close drawer on route change
  useEffect(() => {
    setDrawerOpen(false)
  }, [location.pathname])
  const sideStyle = (active) => ({
    display: "flex", alignItems: "center", gap: 10,
    padding: "8px 10px", borderRadius: 7, border: "none", width: "100%",
    textAlign: "left", fontSize: 13, fontWeight: 500, cursor: "pointer",
    color: active ? T.cyan : T.textDim,
    background: active ? `${T.cyan}12` : "transparent",
    transition: "all 0.15s",
    textDecoration: 'none',
  })
  const topLinkStyle = (active) => ({
    padding: "6px 14px",
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 500,
    color: active ? T.cyan : T.textDim,
    background: active ? `${T.cyan}12` : "transparent",
    textDecoration: 'none',
    transition: 'all 0.15s',
    whiteSpace: 'nowrap',
  })
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      {/* Mobile drawer */}
      <MobileDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        section={section}
        sidebar={sidebar}
        location={location}
      />
      {/* Top bar */}
      <header style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: isTablet ? "10px 16px" : "12px 24px",
        borderBottom: `1px solid ${T.border}`,
        background: T.bgCard, flexShrink: 0, zIndex: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: isTablet ? 12 : 20 }}>
          {/* Hamburger on tablet/mobile */}
          {isTablet && (
            <HamburgerIcon open={drawerOpen} onClick={() => setDrawerOpen(!drawerOpen)} />
          )}
          <NavLink to="/" style={{
            ...serif, fontSize: isTablet ? 14 : 16, fontWeight: 600, letterSpacing: 4,
            color: T.gold, textDecoration: 'none',
          }}>
            MYTHOS
          </NavLink>
          {/* Desktop top nav */}
          {!isTablet && (
            <nav style={{ display: "flex", gap: 4 }}>
              {topNavItems.map((n) => {
                const isHome = n.to === '/'
                const active = isHome
                  ? (section === 'home' || location.pathname === '/')
                  : location.pathname.startsWith(n.to)
                return (
                  <NavLink
                    key={n.label}
                    to={n.to}
                    style={topLinkStyle(active)}
                  >
                    {n.label}
                  </NavLink>
                )
              })}
            </nav>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {!isTablet && (
            <a href="/auth/logout" style={{
              padding: "5px 12px", border: `1px solid ${T.border}`, borderRadius: 5,
              fontSize: 12, color: T.textMuted, textDecoration: 'none',
            }}>logout</a>
          )}
        </div>
      </header>
      {/* Account context strip — finance only */}
      {showAccountStrip && <AccountStrip />}
      {/* Body */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Desktop sidebar — only when section has one and not tablet */}
        {sidebar && !isTablet && (
          <nav style={{
            width: 200, background: T.bgCard, borderRight: `1px solid ${T.border}`,
            padding: "16px 0", flexShrink: 0, overflowY: "auto",
          }}>
            {sidebar.map((group, si) => (
              <div key={group.label}>
                {si > 0 && <hr style={{ border: "none", borderTop: `1px solid ${T.border}`, margin: "8px 12px" }} />}
                <div style={{ padding: "0 12px" }}>
                  <div style={{
                    fontSize: 10, textTransform: "uppercase", letterSpacing: "1.2px",
                    color: T.textMuted, padding: "8px 8px 4px",
                  }}>{group.label}</div>
                  {group.items.map((item) => (
                    <NavLink key={item.to} to={item.to}
                      style={({ isActive }) => sideStyle(isActive)}>
                      <span style={{ fontSize: 15, width: 18, textAlign: "center" }}>{item.icon}</span>
                      {item.label}
                    </NavLink>
                  ))}
                </div>
              </div>
            ))}
          </nav>
        )}
        {/* Main content */}
        <main style={{
          flex: 1,
          overflowY: "auto",
          padding: isTablet ? 16 : 24,
        }}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
// ── Export with Provider ───────────────────────────────────
export default function CommandCenter() {
  return (
    <AccountProvider>
      <CommandCenterInner />
    </AccountProvider>
  )
}
