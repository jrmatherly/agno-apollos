'use client'

import { useStore } from '@/store'
import { SpecialistChip } from './SpecialistChip'
import { ToolsDropdown } from './ToolsDropdown'
import { IconType } from '@/components/ui/icon/types'

interface ChipConfig {
  id: string
  label: string
  icon: IconType
}

const CHIPS: ChipConfig[] = [
  { id: 'web-search-agent', label: 'Search', icon: 'search' },
  { id: 'data-agent', label: 'Data', icon: 'database' },
  { id: 'knowledge-agent', label: 'Knowledge', icon: 'file' }
]

export function SpecialistBar() {
  const { activeSpecialists, toggleSpecialist } = useStore()

  return (
    <div className="mx-auto flex w-full max-w-2xl items-center gap-2 px-1 font-geist">
      {CHIPS.map((chip) => (
        <SpecialistChip
          key={chip.id}
          id={chip.id}
          label={chip.label}
          icon={chip.icon}
          active={activeSpecialists.includes(chip.id)}
          onToggle={toggleSpecialist}
        />
      ))}
      <ToolsDropdown />
    </div>
  )
}
