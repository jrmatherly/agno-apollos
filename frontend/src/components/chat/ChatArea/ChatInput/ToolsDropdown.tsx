'use client'

import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import Icon from '@/components/ui/icon'
import { useStore } from '@/store'
import { toast } from 'sonner'

interface ToolItem {
  id: string
  label: string
  badge?: string
  disabled?: boolean
}

const TOOL_ITEMS: ToolItem[] = [
  { id: 'reasoning-agent', label: 'Reasoning', badge: 'Deep' },
  { id: 'm365-agent', label: 'Microsoft 365' }
]

export function ToolsDropdown() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const { activeSpecialists, toggleSpecialist, m365Connected } = useStore()

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleToggle = (item: ToolItem) => {
    if (item.id === 'm365-agent' && !m365Connected) {
      toast.info('Connect your Microsoft 365 account in Settings to enable.')
      return
    }
    toggleSpecialist(item.id)
  }

  const items = TOOL_ITEMS.map((item) => ({
    ...item,
    disabled: item.id === 'm365-agent' && !m365Connected,
    badge: item.id === 'm365-agent' && !m365Connected ? 'Connect' : item.badge
  }))

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={cn(
          'flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors',
          open
            ? 'border-brand/40 bg-brand/15 text-brand'
            : 'border-primary/15 bg-primaryAccent text-muted hover:border-primary/30'
        )}
      >
        <Icon type="settings" size="xxs" />
        <span>Tools</span>
        <Icon type="chevron-down" size="xxs" />
      </button>

      {open && (
        <div className="absolute bottom-full left-0 mb-2 w-52 rounded-xl border border-primary/15 bg-primaryAccent p-1 shadow-lg backdrop-blur-lg">
          {items.map((item) => {
            const isActive = activeSpecialists.includes(item.id)
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleToggle(item)}
                className={cn(
                  'flex w-full items-center justify-between rounded-lg px-3 py-2 text-xs font-medium transition-colors',
                  item.disabled
                    ? 'cursor-not-allowed opacity-50'
                    : 'hover:bg-accent',
                  isActive && !item.disabled && 'text-brand'
                )}
              >
                <span className="flex items-center gap-2">
                  {item.label}
                  {item.badge && (
                    <span
                      className={cn(
                        'rounded-full px-1.5 py-0.5 text-[10px] font-medium leading-none',
                        item.badge === 'Connect'
                          ? 'bg-muted/20 text-muted'
                          : 'bg-brand/20 text-brand'
                      )}
                    >
                      {item.badge}
                    </span>
                  )}
                </span>
                {isActive && !item.disabled && (
                  <Icon type="check" size="xxs" className="text-brand" />
                )}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
