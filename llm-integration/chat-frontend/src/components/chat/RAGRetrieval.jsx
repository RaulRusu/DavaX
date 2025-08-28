// src/components/chat/RAGRetrieval.jsx
import React, { useMemo, useRef } from 'react'
import { useHoverDisclosure } from '../../hooks/useHoverDisclosure'
import { useDismissableLayer } from '../../hooks/useDismissableLayer'
import HoverPanel from '../common/HoverPanel'

function topK(payload, k = 5) {
  const r = payload?.results
  if (!r || !r.ids || !r.ids[0]) return []
  const list = []
  const ids = r.ids[0]
  const metas = r.metadatas?.[0] || []
  const dists = r.distances?.[0] || []

  for (let i = 0; i < Math.min(k, ids.length); i++) {
    list.push({
      id: ids[i],
      title: metas[i]?.title || ids[i],
      distance: typeof dists[i] === 'number' ? dists[i] : null,
      document: r.documents?.[0]?.[i] || ''
    })
  }
  return list
}

function toCosinePercent(distance) {
  if (typeof distance !== 'number') return '—'
  const sim = (1 - distance) * 100
  return `${sim.toFixed(0)}%`
}

function toInversePercent(distance) {
  if (typeof distance !== 'number') return '—'
  const pct = 100 / (1 + Math.max(0, distance))
  return `${pct.toFixed(0)}%`
}

function scoreText(distance, metric = 'cosine') {
  return metric === 'cosine'
    ? toCosinePercent(distance)
    : toInversePercent(distance)
}

export default function RAGRetrieval({ event }) {
  const p = event?.payload || {}
  const picks = useMemo(() => topK(p, 3), [p])
  const hover = useHoverDisclosure({ openDelay: 350, closeDelay: 120 })
  const panelRef = useRef(null)
  useDismissableLayer({ open: hover.open, onDismiss: hover.closeNow, panelRef })

  return (
    <div className="flex justify-start">
      <div
        className="relative bg-white/5 text-white/90 rounded-2xl rounded-bl-sm px-4 py-2 max-w-[80%] text-sm"
        onMouseEnter={hover.onMouseEnter}
        onMouseLeave={hover.onMouseLeave}
      >
        {/* One-line preview: show top 2-3 titles */}
        <div className="flex items-center gap-2 min-w-0">
          <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-sky-500/20 shrink-0">
            <span>📚</span><span>RAG retrieval</span>
          </span>
          <div className="text-xs text-white/80 truncate">
            {picks.length ? picks.map(x => x.title).join(', ') : 'no results'}
          </div>
        </div>

        {hover.open && (
          <HoverPanel ref={panelRef} width="min(42rem, 95vw)">
            <div className="p-3 border-b border-white/10 flex items-center justify-between">
              <div className="text-xs text-white/70">Top candidates</div>
              <button className="text-xs text-white/60 hover:text-white/90" onClick={hover.closeNow}>✕</button>
            </div>
            <div className="p-3 space-y-3">
              {topK(p, 8).map((x, i) => (
                <div key={x.id} className="border border-white/10 rounded-lg p-2">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-white/90">{i+1}. {x.title}</div>
                    <div className="text-[11px] text-white/50">score: {scoreText(x.distance)}</div>
                  </div>
                  {x.document && (
                    <div className="mt-1 text-xs text-white/70 line-clamp-3 whitespace-pre-wrap">
                      {x.document.slice(0, 360)}{x.document.length > 360 ? '…' : ''}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </HoverPanel>
        )}
      </div>
    </div>
  )
}
