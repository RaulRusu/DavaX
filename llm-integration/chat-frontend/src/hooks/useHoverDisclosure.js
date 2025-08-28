import { useCallback, useEffect, useRef, useState } from 'react'

export function useHoverDisclosure({
  openDelay = 700,
  closeDelay = 120,
  initialOpen = false,
} = {}) {
  const [open, setOpen] = useState(initialOpen)
  const enterTimer = useRef(null)
  const leaveTimer = useRef(null)

  const clearTimers = useCallback(() => {
    if (enterTimer.current) clearTimeout(enterTimer.current)
    if (leaveTimer.current) clearTimeout(leaveTimer.current)
    enterTimer.current = null
    leaveTimer.current = null
  }, [])

  const onMouseEnter = useCallback(() => {
    if (leaveTimer.current) clearTimeout(leaveTimer.current)
    enterTimer.current = setTimeout(() => setOpen(true), openDelay)
  }, [openDelay])

  const onMouseLeave = useCallback(() => {
    if (enterTimer.current) clearTimeout(enterTimer.current)
    leaveTimer.current = setTimeout(() => setOpen(false), closeDelay)
  }, [closeDelay])

  const openNow = useCallback(() => {
    clearTimers()
    setOpen(true)
  }, [clearTimers])

  const closeNow = useCallback(() => {
    clearTimers()
    setOpen(false)
  }, [clearTimers])

  useEffect(() => () => clearTimers(), [clearTimers])

  return {
    open,
    setOpen,
    onMouseEnter,
    onMouseLeave,
    openNow,
    closeNow,
  }
}
