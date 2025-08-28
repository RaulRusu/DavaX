import React from 'react'
import clsx from 'clsx'

export default function MessageBubble({ role = 'assistant', text = '' }) {
  const isUser = role === 'user'
  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={clsx(
          'max-w-[80%] rounded-2xl px-4 py-3 leading-relaxed text-sm whitespace-pre-wrap',
          isUser
            ? 'bg-accent text-white rounded-br-sm'
            : 'bg-white/5 text-white/90 rounded-bl-sm'
        )}
      >
        {text}
      </div>
    </div>
  )
}
