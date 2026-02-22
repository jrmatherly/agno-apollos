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
          'group flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition-all',
          open
            ? 'border-brand/30 bg-brand/10 text-brand'
            : 'border-white/10 bg-white/5 text-slate-400 hover:border-white/20 hover:bg-white/10 hover:text-slate-200'
        )}
      >
        <Icon
          type="settings"
          size="xxs"
          className="text-slate-500 transition-colors group-hover:text-purple-400"
        />
        <span>Tools</span>
        <Icon type="chevron-down" size="xxs" className="ml-0.5 opacity-50" />
      </button>

      {open && (
        <div className="absolute bottom-full left-0 mb-2 w-52 rounded-xl border border-white/10 bg-background/90 p-1 shadow-lg backdrop-blur-2xl">
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
                    : 'hover:bg-white/5',
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
