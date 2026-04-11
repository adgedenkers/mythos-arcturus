import { useState, useEffect, useCallback, useRef, createContext, useContext } from 'react'
import { T, mono } from '../../styles/theme'

/**
 * Toast notification system
 * 
 * Setup (once, in App or layout):
 *   <ToastProvider>
 *     <App />
 *   </ToastProvider>
 * 
 * Usage in any component:
 *   const toast = useToast()
 *   toast.success('Bill matched successfully')
 *   toast.error('Failed to save')
 *   toast.info('Pattern learned: PROGRESSIVE INS')
 */

const ToastContext = createContext(null)

let toastId = 0

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be inside <ToastProvider>')
  return ctx
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, variant = 'info', duration = 3500) => {
    const id = ++toastId
    setToasts((prev) => [...prev, { id, message, variant }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, duration)
    return id
  }, [])

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const api = {
    success: (msg, dur) => addToast(msg, 'success', dur),
    error: (msg, dur) => addToast(msg, 'error', dur || 5000),
    info: (msg, dur) => addToast(msg, 'info', dur),
    warn: (msg, dur) => addToast(msg, 'warning', dur),
    dismiss,
  }

  return (
    <ToastContext.Provider value={api}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  )
}

function ToastContainer({ toasts, onDismiss }) {
  if (!toasts.length) return null

  return (
    <div style={{
      position: 'fixed',
      bottom: 20,
      right: 20,
      zIndex: 300,
      display: 'flex',
      flexDirection: 'column-reverse',
      gap: 8,
      maxWidth: 380,
    }}>
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onDismiss={() => onDismiss(t.id)} />
      ))}
    </div>
  )
}

function ToastItem({ toast, onDismiss }) {
  const colors = {
    success: { accent: T.green, bg: `${T.green}12`, icon: '✓' },
    error:   { accent: T.red,   bg: `${T.red}12`,   icon: '✕' },
    warning: { accent: T.amber, bg: `${T.amber}12`, icon: '⚠' },
    info:    { accent: T.cyan,  bg: `${T.cyan}12`,  icon: 'ℹ' },
  }
  const c = colors[toast.variant] || colors.info

  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: 10,
      padding: '10px 14px',
      background: T.bgCard,
      border: `1px solid ${c.accent}30`,
      borderLeft: `3px solid ${c.accent}`,
      borderRadius: 6,
      boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
      animation: 'toast-in 0.2s ease',
    }}>
      <span style={{ color: c.accent, fontSize: 13, fontWeight: 700, marginTop: 1 }}>
        {c.icon}
      </span>
      <span style={{
        ...mono,
        fontSize: 12,
        color: T.text,
        flex: 1,
        lineHeight: 1.4,
      }}>
        {toast.message}
      </span>
      <button
        onClick={onDismiss}
        style={{
          background: 'none',
          border: 'none',
          color: T.textMuted,
          fontSize: 12,
          cursor: 'pointer',
          padding: '0 2px',
          lineHeight: 1,
        }}
      >
        ✕
      </button>
      <style>{`
        @keyframes toast-in {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}
