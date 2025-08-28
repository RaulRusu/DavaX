import React, { useRef } from 'react'
import { useHoverDisclosure } from '../../hooks/useHoverDisclosure'
import { useDismissableLayer } from '../../hooks/useDismissableLayer'
import HoverPanel from '../common/HoverPanel'

export default function RAGQuery({ event }) {
  const p = event?.payload || {}
  const q = p.query || ''
  const retrievers = p.retrievers || []
  const fusion = p.fusion
  const filters = p.filters || {}

  const hover = useHoverDisclosure({ openDelay: 400, closeDelay: 120 })
  const panelRef = useRef(null)
  useDismissableLayer({ open: hover.open, onDismiss: hover.closeNow, panelRef })

  return (
    <div className="flex justify-start">
      <div
        className="relative bg-white/5 text-white/90 rounded-2xl rounded-bl-sm px-4 py-2 max-w-[80%] text-sm"
        onMouseEnter={hover.onMouseEnter}
        onMouseLeave={hover.onMouseLeave}
      >
        {/* One-line preview */}
        <div className="flex items-center gap-2 min-w-0">
          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-indigo-500/20 shrink-0">
            <span>🔎</span><span>RAG query</span>
          </span>
          <div className="text-xs text-white/80 truncate">„{q}”</div>
          <div className="text-[10px] text-white/40 shrink-0 ml-2">
            {retrievers.join('+')}{fusion ? ` · ${fusion}` : ''}
          </div>
        </div>

        {hover.open && (
          <HoverPanel ref={panelRef}>
            <div className="p-3 border-b border-white/10 flex items-center justify-between">
              <div className="text-xs text-white/70">RAG query details</div>
              <button className="text-xs text-white/60 hover:text-white/90" onClick={hover.closeNow}>✕</button>
            </div>
            <div className="p-3 space-y-2">
              <div className="text-[11px] text-white/50">Query</div>
              <div className="text-sm text-white/90">„{q}”</div>

              <div className="text-[11px] text-white/50 mt-3">Retrievers</div>
              <div className="text-sm text-white/80">{retrievers.join(' + ') || '—'}</div>

              {fusion && <>
                <div className="text-[11px] text-white/50 mt-3">Fusion</div>
                <div className="text-sm text-white/80">{fusion}</div>
              </>}

              {filters && Object.keys(filters).length > 0 && (
                <>
                  <div className="text-[11px] text-white/50 mt-3">Filters</div>
                  <pre className="text-xs whitespace-pre-wrap bg-black/30 rounded-lg p-2 overflow-x-auto">
                    {JSON.stringify(filters, null, 2)}
                  </pre>
                </>
              )}
            </div>
          </HoverPanel>
        )}
      </div>
    </div>
  )
}
