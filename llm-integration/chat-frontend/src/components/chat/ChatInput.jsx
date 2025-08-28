import React, { useState } from 'react'
import { useChat } from '../../store/ChatProvider.jsx'

export default function ChatInput() {
  const { sendMessage } = useChat()
  const [value, setValue] = useState('')
  const [busy, setBusy] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    const text = value.trim()
    if (!text) return
    setBusy(true)
    setValue('')
    try {
      await sendMessage(text)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={onSubmit} className="rounded-xl border border-white/10 bg-white/5 p-2">
      <div className="flex items-end gap-2">
        <textarea
          className="min-h-[48px] max-h-40 flex-1 bg-transparent outline-none resize-none px-3 py-2 text-sm placeholder:text-white/40"
          placeholder="Message the model..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <button
          disabled={busy}
          className="rounded-lg px-3 py-2 bg-white/10 text-white text-sm border border-white/10 disabled:opacity-50"
          title="Send"
        >
          Send
        </button>
      </div>
    </form>
  )
}
