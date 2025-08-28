import { useEffect } from 'react'

export function useDismissableLayer({ open, onDismiss, panelRef }) {
  useEffect(() => {
    if (!open) return
    const onKey = (e) => { if (e.key === 'Escape') onDismiss?.() }
    const onClick = (e) => {
      if (!panelRef?.current) return
      if (!panelRef.current.contains(e.target)) onDismiss?.()
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener('mousedown', onClick)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('mousedown', onClick)
    }
  }, [open, onDismiss, panelRef])
}
