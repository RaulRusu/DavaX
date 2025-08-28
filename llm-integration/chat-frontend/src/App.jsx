import React, { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar.jsx'
import ChatWindow from './components/ChatWindow.jsx'

export default function App() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="h-dvh w-screen grid grid-cols-1 md:grid-cols-[minmax(20rem,20%)_1fr]">
      {/* Desktop sidebar */}
      <div className="hidden md:flex">
        <Sidebar />
      </div>

      {/* Mobile drawer */}
      <div className={`md:hidden ${mobileOpen ? '' : 'pointer-events-none'}`}>
        {/* Backdrop */}
        <div
          onClick={() => setMobileOpen(false)}
          className={`fixed inset-0 bg-black/50 transition-opacity duration-200 ${mobileOpen ? 'opacity-100' : 'opacity-0'} z-40`}
        />
        {/* Panel */}
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Sidebar"
          className={`fixed inset-y-0 left-0 w-[80vw] max-w-80 bg-sidebar border-r border-white/10 shadow-xl transition-transform duration-200 ease-out ${mobileOpen ? 'translate-x-0' : '-translate-x-full'} z-50`}
        >
          <Sidebar onClose={() => setMobileOpen(false)} onNavigate={() => setMobileOpen(false)} />
        </div>
      </div>

      {/* Chat area */}
      <ChatWindow onOpenSidebar={() => setMobileOpen(true)} />
    </div>
  )
}
