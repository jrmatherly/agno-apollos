'use client'

import { cn } from '@/lib/utils'
import Icon from '@/components/ui/icon'
import { IconType } from '@/components/ui/icon/types'

interface SpecialistChipProps {
  id: string
  label: string
  icon: IconType
  active: boolean
  disabled?: boolean
  badge?: string
  hoverColorClass?: string
  onToggle: (id: string) => void
  onDisabledClick?: () => void
}

export function SpecialistChip({
  id,
  label,
  icon,
  active,
  disabled = false,
  badge,
  hoverColorClass,
  onToggle,
  onDisabledClick
}: SpecialistChipProps) {
  const handleClick = () => {
    if (disabled) {
      onDisabledClick?.()
      return
    }
    onToggle(id)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={cn(
        'group flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition-all',
        disabled && 'cursor-not-allowed opacity-50',
        active
          ? 'border-brand/30 bg-brand/10 text-brand'
          : 'border-white/10 bg-white/5 text-slate-400 hover:border-white/20 hover:bg-white/10 hover:text-slate-200'
      )}
    >
      <Icon
        type={icon}
        size="xxs"
        className={cn(
          'text-slate-500 transition-colors',
          active && 'text-brand',
          !active && hoverColorClass
        )}
      />
      <span>{label}</span>
      {badge && (
        <span
          className={cn(
            'rounded-full px-1.5 py-0.5 text-[10px] font-medium leading-none',
            badge === 'Connect'
              ? 'bg-muted/20 text-muted'
              : 'bg-brand/20 text-brand'
          )}
        >
          {badge}
        </span>
      )}
    </button>
  )
}
