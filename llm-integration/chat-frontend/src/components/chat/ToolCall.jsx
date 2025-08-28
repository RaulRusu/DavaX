// src/components/chat/ToolCall.jsx
import React, { useRef } from 'react'
import { useHoverDisclosure } from '../../hooks/useHoverDisclosure'
import { useDismissableLayer } from '../../hooks/useDismissableLayer'
import HoverPanel from '../common/HoverPanel'

function pretty(obj) {
  try { return JSON.stringify(obj, null, 2) } catch { return String(obj) }
}
function inlinePreview(args, max = 80) {
  const parts = Object.entries(args || {}).map(([k, v]) => {
    const val = typeof v === 'string' ? v : JSON.stringify(v)
    return `${k}=${val}`
  })
  const s = parts.join(' ')
  return s.length > max ? s.slice(0, max) + '…' : s || 'no-args'
}

export default function ToolCall({ event }) {
  const name = event?.payload?.name || event?.payload?.function_name || 'tool'
  const args = event?.payload?.arguments ?? {}
  const callId = event?.payload?.call_id
  const pending = event?.pending

  // reuse logic here
  const hover = useHoverDisclosure({ openDelay: 700, closeDelay: 120 })
  const panelRef = useRef(null)
  useDismissableLayer({ open: hover.open, onDismiss: hover.closeNow, panelRef })

  return (
    <div className="flex justify-start">
      <div
        className="relative bg-white/5 text-white/90 rounded-2xl rounded-bl-sm px-4 py-2 max-w-[80%] text-sm"
        onMouseEnter={hover.onMouseEnter}
        onMouseLeave={hover.onMouseLeave}
      >
        {/* single-row preview */}
        <div className="flex items-center gap-2 min-w-0">
          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-white/10 shrink-0">
            <span>🛠️</span><span>Tool call</span>
          </span>
          <code className="text-white/80 text-xs shrink-0">{name}</code>
          {pending && <span className="text-[11px] text-white/50 shrink-0">running…</span>}
          <div className="text-xs text-white/70 truncate ml-1">{inlinePreview(args)}</div>
        </div>

        {/* floating details (reusable!) */}
        {hover.open && (
          <HoverPanel ref={panelRef}>
            <div className="p-3 border-b border-white/10 flex items-center gap-2 justify-between">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-white/10">
                  <span>🛠️</span><span>Tool call</span>
                </span>
                <code className="text-white/80 text-xs">{name}</code>
                {callId && (
                  <span className="text-[10px] text-white/40 ml-2">call_id: <code>{callId}</code></span>
                )}
              </div>
              <button className="text-xs text-white/60 hover:text-white/90" onClick={hover.closeNow}>✕</button>
            </div>
            <div className="p-3">
              <div className="text-[11px] uppercase tracking-wide text-white/40 mb-1">Arguments</div>
              <pre className="text-xs whitespace-pre-wrap bg-black/30 rounded-lg p-2 overflow-x-auto">
                {pretty(args)}
              </pre>
            </div>
          </HoverPanel>
        )}
      </div>
    </div>
  )
}
