import { MessageSquare, Bot } from 'lucide-react'
import { useStore } from '@/store'

const SessionBlankState = () => {
  const { selectedEndpoint, isEndpointActive } = useStore()

  const errorMessage = (() => {
    switch (true) {
      case !isEndpointActive:
        return 'Endpoint is not connected. Please connect the endpoint to see the history.'
      case !selectedEndpoint:
        return 'Select an endpoint to see the history.'
      default:
        return 'Start a new conversation with Apollos to see your history here.'
    }
  })()

  return (
    <div className="group relative flex flex-col items-center justify-center overflow-hidden rounded-xl border border-white/5 bg-gradient-to-b from-slate-900/60 to-slate-900/40 p-4 text-center transition-colors hover:border-white/10">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-sky-900/10 to-transparent opacity-50" />
      <div className="relative mb-1 h-12 w-12">
        <MessageSquare className="absolute left-0 top-0 h-10 w-10 -rotate-12 transform text-slate-700 transition-transform group-hover:-rotate-6" />
        <Bot className="absolute bottom-0 right-0 h-10 w-10 rotate-12 transform text-sky-900/50 blur-[1px] transition-transform group-hover:rotate-6" />
      </div>
      <div className="relative z-10 space-y-1">
        <h3 className="text-sm font-medium text-slate-300">No Recent Chats</h3>
        <p className="px-2 text-xs leading-relaxed text-slate-400">
          {errorMessage}
        </p>
      </div>
    </div>
  )
}

export default SessionBlankState
