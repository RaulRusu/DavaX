import React, { useState, useEffect, useRef } from 'react'
import { useChat } from '../store/ChatProvider.jsx'
import ChatListItem from './chat/ChatListItem.jsx'

export default function Sidebar({ onClose, onNavigate }) {
  const { chats, activeId, createChat, selectChat } = useChat()
  const [naming, setNaming] = useState(false)
  const [title, setTitle] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    if (naming && inputRef.current) inputRef.current.focus()
  }, [naming])

  const handleCreate = async () => {
    const name = title.trim() || 'New chat'
    const chat = await createChat(name)
    setTitle('')
    setNaming(false)
    onNavigate && onNavigate()
  }

  const handleSelect = (id) => {
    selectChat(id)
    onNavigate && onNavigate()
  }

  return (
    <aside className="bg-sidebar border-r border-white/10 flex flex-col h-full w-full">
      <div className="p-3 flex items-center gap-2">
        <button
          onClick={onClose}
          className="md:hidden p-2 rounded-lg hover:bg-white/10"
          aria-label="Close menu"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="text-white/80">
            <line x1="18" y1="6" x2="6" y2="18" strokeWidth="2" />
            <line x1="6" y1="6" x2="18" y2="18" strokeWidth="2" />
          </svg>
        </button>

        {!naming ? (
          <button
            onClick={() => setNaming(true)}
            className="w-full rounded-md px-3 py-2 text-sm font-medium bg-white/10 hover:bg-white/15 transition"
          >
            + New chat
          </button>
        ) : (
          <div className="w-full grid items-center gap-2">
            <input
              ref={inputRef}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Chat title…"
              className="flex-1 rounded-md bg-white/5 border border-white/10 px-3 py-2 text-sm outline-none placeholder:text-white/40"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={handleCreate}
                className="rounded-md px-3 py-2 text-sm bg-accent text-white"
              >
                Create
              </button>
              <button
                onClick={() => { setNaming(false); setTitle('') }}
                className="rounded-md px-3 py-2 text-sm bg-white/10"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="px-3 pt-3 pb-2 text-xs uppercase tracking-wide text-white/50">
        Recent
      </div>

      <nav className="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
        {chats.length === 0 && (
          <div className="text-white/50 text-sm px-3 py-2">No chats yet.</div>
        )}
        {chats.map(c => (
          <div key={c.id} onClick={() => handleSelect(c.id)}>
            <ChatListItem title={c.title || 'Untitled chat'} active={c.id === activeId} />
          </div>
        ))}
      </nav>

      <div className="p-3 border-t border-white/10 text-xs text-white/50">
        <div className="flex items-center gap-2">
          <div className="size-2 rounded-full bg-green-500"></div>
          Chat (demo)
        </div>
      </div>
    </aside>
  )
}
