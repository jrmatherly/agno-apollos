'use client'

import ChatInput from './ChatInput'
import { SpecialistBar } from './ChatInput/SpecialistBar'
import MessageArea from './MessageArea'
const ChatArea = () => {
  return (
    <main className="relative flex flex-1 flex-col items-center justify-center p-6 lg:p-8 xl:p-10">
      <div className="glass-panel-premium blue-rim-glow relative flex h-full w-full max-w-5xl flex-col overflow-hidden rounded-3xl">
        {/* Top Gradient Line */}
        <div className="absolute left-0 right-0 top-0 z-20 h-[1px] bg-gradient-to-r from-transparent via-sky-200/20 to-transparent" />

        <MessageArea />

        {/* Input Area */}
        <div className="absolute bottom-8 left-0 right-0 bg-transparent px-8">
          <div className="mx-auto max-w-3xl">
            <ChatInput />
            <SpecialistBar />
            {/* Footer Status */}
            <div className="mt-4 flex items-center justify-center space-x-2 opacity-60">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
              <p className="text-[9px] font-medium uppercase tracking-[0.2em] text-slate-400">
                Powered by{' '}
                <span className="text-emerald-400 drop-shadow-[0_0_3px_rgba(52,211,153,0.5)]">
                  Apollos
                </span>{' '}
                AgentOS
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default ChatArea
