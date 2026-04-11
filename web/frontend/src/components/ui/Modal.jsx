import { useEffect, useCallback } from 'react'
import { T, mono, serif } from '../../styles/theme'

/**
 * Modal — overlay dialog for confirmations, detail views, forms
 * 
 * Usage:
 *   <Modal open={showModal} onClose={() => setShowModal(false)} title="Confirm Match">
 *     <p>Match Progressive → PROGRESSIVE INS?</p>
 *     <Modal.Actions>
 *       <Button variant="ghost" onClick={cancel}>Cancel</Button>
 *       <Button variant="primary" onClick={confirm}>Confirm</Button>
 *     </Modal.Actions>
 *   </Modal>
 */
function Modal({ open, onClose, title, width = 480, children }) {
  const handleEsc = useCallback((e) => {
    if (e.key === 'Escape' && onClose) onClose()
  }, [onClose])

  useEffect(() => {
    if (open) {
      document.addEventListener('keydown', handleEsc)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = ''
    }
  }, [open, handleEsc])

  if (!open) return null

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 200,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
    }}>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0,0,0,0.65)',
          backdropFilter: 'blur(2px)',
        }}
      />
      {/* Dialog */}
      <div style={{
        position: 'relative',
        width: '100%',
        maxWidth: width,
        maxHeight: '85vh',
        overflowY: 'auto',
        background: T.bgCard,
        border: `1px solid ${T.borderLight}`,
        borderRadius: 10,
        boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
      }}>
        {/* Header */}
        {title && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 20px',
            borderBottom: `1px solid ${T.border}`,
          }}>
            <h3 style={{
              ...serif,
              fontSize: 15,
              fontWeight: 600,
              letterSpacing: 1.5,
              color: T.text,
              margin: 0,
            }}>
              {title}
            </h3>
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                color: T.textMuted,
                fontSize: 18,
                cursor: 'pointer',
                padding: '2px 6px',
                borderRadius: 4,
                lineHeight: 1,
              }}
            >
              ✕
            </button>
          </div>
        )}
        {/* Body */}
        <div style={{ padding: '16px 20px' }}>
          {children}
        </div>
      </div>
    </div>
  )
}

/**
 * Modal.Actions — footer action bar inside a modal
 * Usage: <Modal.Actions><Button>Cancel</Button><Button>OK</Button></Modal.Actions>
 */
Modal.Actions = function ModalActions({ children, style: sx }) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 8,
      paddingTop: 16,
      marginTop: 16,
      borderTop: `1px solid ${T.border}`,
      ...sx,
    }}>
      {children}
    </div>
  )
}

export default Modal
