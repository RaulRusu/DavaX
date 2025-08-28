import React from 'react'

export default function ChatListItem({ title, active, onClick }) {
  const base =
    'group flex items-center gap-2 px-3 py-2 rounded-md cursor-pointer text-sm text-white/80 hover:bg-white/5'
  const activeClass = active ? ' bg-white/10 text-white' : ''
  return (
    <div className={base + activeClass} onClick={onClick}>
      <div className="size-2 rounded-full bg-white/30 group-hover:bg-white/50"></div>
      <div className="truncate">{title}</div>
    </div>
  )
}
