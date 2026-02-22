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
        'flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors',
        disabled && 'cursor-not-allowed opacity-50',
        active
          ? 'border-brand/40 bg-brand/15 text-brand'
          : 'border-primary/15 bg-primaryAccent text-muted hover:border-primary/30'
      )}
    >
      <Icon type={icon} size="xxs" />
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
