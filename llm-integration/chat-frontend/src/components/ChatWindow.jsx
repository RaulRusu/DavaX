import React, { useMemo, useState } from 'react'
import MessageBubble from './chat/MessageBubble.jsx'
import ToolCall from './chat/ToolCall.jsx'
import ChatInput from './chat/ChatInput.jsx'
import ToolResult from './chat/ToolResult.jsx'
import RAGQuery from './chat/RAGQuery.jsx'
import RAGRetrieval from './chat/RAGRetrieval.jsx'
import { useChat } from '../store/ChatProvider.jsx'

const STEP_TYPES = new Set([
  'function_call',
  'function_call_output',
  'rag_query',
  'rag_retrieval'
])

export default function ChatWindow({ onOpenSidebar }) {
  const { chats, activeId, messages } = useChat()
  const active = chats.find(c => c.id === activeId)
  const list = messages[activeId] || []

  // Build segments: attach any contiguous "step" events to the next message_text.
  const segments = useMemo(() => {
    const result = []
    let stepsBuffer = []

    for (const m of list) {
      if (STEP_TYPES.has(m.event_type)) {
        stepsBuffer.push(m)
        continue
      }
      if (m.event_type === 'message_text') {
        result.push({ message: m, steps: stepsBuffer })
        stepsBuffer = []
      } else {
        // Unknown event type: just flush it as its own segment to be safe
        result.push({ message: null, steps: [m] })
      }
    }

    // If the list ends with steps and no trailing message, you can either drop or show them.
    // We'll append as a segment without a message:
    if (stepsBuffer.length) result.push({ message: null, steps: stepsBuffer })

    return result
  }, [list])

  // Track open/closed per assistant message id
  const [openSteps, setOpenSteps] = useState({}) // { [messageId]: boolean }
  const toggle = (id) => setOpenSteps(s => ({ ...s, [id]: !s[id] }))

  return (
    <section className="flex flex-col h-screen">
      {/* Top bar */}
      <header className="relative z-10 h-14 flex items-center justify-between px-4 border-b border-white/10 bg-surface/60 backdrop-blur">
        <div className="flex items-center gap-2">
          <button
            className="md:hidden p-2 rounded-lg hover:bg-white/10"
            aria-label="Open menu"
            onClick={onOpenSidebar}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="text-white/80">
              <line x1="3" y1="6" x2="21" y2="6" strokeWidth="2" />
              <line x1="3" y1="12" x2="21" y2="12" strokeWidth="2" />
              <line x1="3" y1="18" x2="21" y2="18" strokeWidth="2" />
            </svg>
          </button>
          <div className="font-medium">{active?.title || 'New chat'}</div>
        </div>
        <div className="text-xs text-white/50">Static header</div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
        <div className="mx-auto max-w-3xl space-y-2">
          {segments.map((seg, idx) => {
            const m = seg.message

            // Segment with an attached message
            if (m) {
              const isAssistant = m.role === 'assistant'
              const hasSteps = seg.steps.length > 0
              const isOpen = openSteps[m.id] ?? false

              return (
                <div key={m.id}>
                  {/* Toggle shown ABOVE each assistant message if it has steps */}
                  {isAssistant && hasSteps && (
                    <div className="flex justify-center my-1">
                      <button
                        className="text-xs text-white/60 hover:text-white underline"
                        onClick={() => toggle(m.id)}
                      >
                        {isOpen ? 'Hide steps' : 'See steps'}
                      </button>
                    </div>
                  )}

                  {/* Steps (only for assistant, above the bubble if desired) */}
                  {isAssistant && hasSteps && isOpen && (
                    <div className="space-y-1 mb-1">
                      {seg.steps.map(step => {
                        if (step.event_type === 'function_call') return <ToolCall key={step.id} event={step} />
                        if (step.event_type === 'function_call_output') return <ToolResult key={step.id} event={step} />
                        if (step.event_type === 'rag_query') return <RAGQuery key={step.id} event={step} />
                        if (step.event_type === 'rag_retrieval') return <RAGRetrieval key={step.id} event={step} />
                        return null
                      })}
                    </div>
                  )}

                  {/* The actual message bubble */}
                  <MessageBubble
                    role={m.role}
                    text={m.payload.content + (m.pending ? ' …' : '')}
                  />
                </div>
              )
            }

            // Segment without a message (dangling steps at start/end)
            return (
              <div key={`steps-${idx}`} className="space-y-1">
                {seg.steps.map(step => {
                  if (step.event_type === 'function_call') return <ToolCall key={step.id} event={step} />
                  if (step.event_type === 'function_call_output') return <ToolResult key={step.id} event={step} />
                  if (step.event_type === 'rag_query') return <RAGQuery key={step.id} event={step} />
                  if (step.event_type === 'rag_retrieval') return <RAGRetrieval key={step.id} event={step} />
                  return null
                })}
              </div>
            )
          })}

          {list.length === 0 && (
            <div className="text-white/40 text-sm">Say hi to start the conversation.</div>
          )}
        </div>
      </main>

      {/* Input */}
      <footer className="px-4 md:px-8 pb-4">
        <div className="mx-auto max-w-3xl">
          <ChatInput />
          <p className="text-[11px] text-white/40 mt-2 text-center">
            Prototype
          </p>
        </div>
      </footer>
    </section>
  )
}
