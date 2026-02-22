'use client'

import * as React from 'react'
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from '@/components/ui/select'
import { useStore } from '@/store'
import { useQueryState } from 'nuqs'
import useChatActions from '@/hooks/useChatActions'

export function ModeSelector() {
  const { mode, setMode, setMessages, setSelectedModel } = useStore()
  const { clearChat } = useChatActions()
  const [, setAgentId] = useQueryState('agent')
  const [, setTeamId] = useQueryState('team')
  const [, setSessionId] = useQueryState('session')

  const handleModeChange = (newMode: 'agent' | 'team') => {
    if (newMode === mode) return

    setMode(newMode)

    setAgentId(null)
    setTeamId(null)
    setSelectedModel('')
    setMessages([])
    setSessionId(null)
    clearChat()
  }

  return (
    <>
      <Select
        defaultValue={mode}
        value={mode}
        onValueChange={(value) => handleModeChange(value as 'agent' | 'team')}
      >
        <SelectTrigger className="h-9 w-full rounded-lg border border-white/5 bg-slate-800/30 text-xs font-medium">
          <SelectValue />
        </SelectTrigger>
        <SelectContent className="border border-white/10 bg-primaryAccent font-sans shadow-lg">
          <SelectItem value="agent" className="cursor-pointer">
            <div className="text-xs font-medium">Agent</div>
          </SelectItem>

          <SelectItem value="team" className="cursor-pointer">
            <div className="text-xs font-medium">Team</div>
          </SelectItem>
        </SelectContent>
      </Select>
    </>
  )
}
