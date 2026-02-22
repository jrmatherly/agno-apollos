'use client'

import { useStore } from '@/store'
import { SpecialistChip } from './SpecialistChip'
import { ToolsDropdown } from './ToolsDropdown'
import { IconType } from '@/components/ui/icon/types'

interface ChipConfig {
  id: string
  label: string
  icon: IconType
  hoverColorClass: string
}

const CHIPS: ChipConfig[] = [
  {
    id: 'web-search-agent',
    label: 'Search',
    icon: 'search',
    hoverColorClass: 'group-hover:text-sky-400'
  },
  {
    id: 'data-agent',
    label: 'Data',
    icon: 'database',
    hoverColorClass: 'group-hover:text-emerald-400'
  },
  {
    id: 'knowledge-agent',
    label: 'Knowledge',
    icon: 'file',
    hoverColorClass: 'group-hover:text-amber-400'
  }
]

export function SpecialistBar() {
  const { activeSpecialists, toggleSpecialist } = useStore()

  return (
    <div className="mt-3 flex items-center gap-2 px-1 font-sans">
      {CHIPS.map((chip) => (
        <SpecialistChip
          key={chip.id}
          id={chip.id}
          label={chip.label}
          icon={chip.icon}
          hoverColorClass={chip.hoverColorClass}
          active={activeSpecialists.includes(chip.id)}
          onToggle={toggleSpecialist}
        />
      ))}
      <ToolsDropdown />
    </div>
  )
}
