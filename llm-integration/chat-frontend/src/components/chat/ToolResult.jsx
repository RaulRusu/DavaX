import React, { useRef } from 'react'
import { useHoverDisclosure } from '../../hooks/useHoverDisclosure'
import { useDismissableLayer } from '../../hooks/useDismissableLayer'
import HoverPanel from '../common/HoverPanel'

function preview(value, max = 160) {
  const s = typeof value === 'string'
    ? value
    : (() => { try { return JSON.stringify(value) } catch { return String(value) } })()
  return s?.length > max ? s.slice(0, max) + '…' : (s ?? 'null')
}

function pretty(obj) {
  try { return JSON.stringify(obj, null, 2) } catch { return String(obj) }
}

export default function ToolResult({ event }) {
  const p = event?.payload || {}
  const tool = p.tool || p.name || 'tool'
  const callId = p.call_id
  const output = p.output ?? p.result_llm

  // Reusable hover logic
  const hover = useHoverDisclosure({ openDelay: 600, closeDelay: 120 })
  const panelRef = useRef(null)
  useDismissableLayer({ open: hover.open, onDismiss: hover.closeNow, panelRef })

  return (
    <div className="flex justify-start">
      <div
        className="relative bg-white/5 text-white/90 rounded-2xl rounded-bl-sm px-4 py-2 max-w-[80%] text-sm"
        onMouseEnter={hover.onMouseEnter}
        onMouseLeave={hover.onMouseLeave}
      >
        {/* Single-line, compact row */}
        <div className="flex items-center gap-2 min-w-0">
          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/20 shrink-0">
            <span>✅</span>
            <span>Tool result</span>
          </span>
          <code className="text-white/80 text-xs shrink-0">{tool}</code>
        </div>

        {/* Floating panel (doesn't change row height) */}
        {hover.open && (
          <HoverPanel ref={panelRef}>
            <div className="p-3 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/20">
                  <span>✅</span>
                  <span>Tool result</span>
                </span>
                <code className="text-white/80 text-xs">{tool}</code>
                {callId && (
                  <span className="text-[10px] text-white/40 ml-2">
                    call_id: <code>{callId}</code>
                  </span>
                )}
              </div>
              <button
                className="text-xs text-white/60 hover:text-white/90"
                onClick={hover.closeNow}
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            <div className="p-3">
              <div className="text-[11px] uppercase tracking-wide text-white/40 mb-1">Raw output</div>
              <pre className="text-xs whitespace-pre-wrap bg-black/30 rounded-lg p-2 overflow-x-auto">
                {pretty(output)}
              </pre>
            </div>
          </HoverPanel>
        )}
      </div>
    </div>
  )
}
