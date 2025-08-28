import React, { forwardRef } from 'react'
import clsx from 'clsx'

// HoverPanel positions an absolutely placed panel relative to its parent (which should be relative).
const HoverPanel = forwardRef(function HoverPanel(
  { children, className, align = 'left', side = 'bottom', offset = 8, width = 'min(36rem, 90vw)', maxHeight = '50vh', border = true },
  ref
) {
  const pos = side === 'top' ? `bottom-full mb-[${offset}px]` : `top-full mt-[${offset}px]`
  const alignClass = align === 'right' ? 'right-0' : 'left-0'
  return (
    <div
      ref={ref}
      className={clsx(
        'absolute z-20',
        alignClass,
        pos,
        'rounded-xl rounded-tl-sm bg-[#0b0b0d]/95 backdrop-blur shadow-xl mt-1',
        border && 'border border-white/10',
        className
      )}
      style={{ width, maxHeight, overflow: 'auto' }}
      role="dialog"
    >
      {children}
    </div>
  )
})

export default HoverPanel
