'use client'

import { motion } from 'framer-motion'
import { Bot, Search, Database, FileText } from 'lucide-react'
import { useStore } from '@/store'

const QUICK_ACTIONS = [
  {
    icon: Search,
    label: 'Search Knowledge Base',
    prompt: 'Search the knowledge base for '
  },
  { icon: Database, label: 'Query Data', prompt: 'Query the data for ' },
  {
    icon: FileText,
    label: 'Web Search',
    prompt: 'Search the web for '
  }
]

const ChatBlankState = () => {
  const { chatInputRef } = useStore()

  const handleQuickAction = (prompt: string) => {
    const input = chatInputRef?.current
    if (input) {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        'value'
      )?.set
      nativeInputValueSetter?.call(input, prompt)
      input.dispatchEvent(new Event('input', { bubbles: true }))
      input.focus()
    }
  }

  return (
    <section
      className="flex flex-col items-center gap-6 font-sans"
      aria-label="Welcome message"
    >
      {/* AI Greeting */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="flex max-w-3xl items-start gap-4"
      >
        <div className="mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl border border-sky-500/20 bg-gradient-to-br from-sky-900/30 to-slate-900/50 shadow-[0_0_15px_rgba(56,189,248,0.15)]">
          <Bot className="h-5 w-5 text-sky-400 opacity-90" />
        </div>
        <div className="glass-bubble-ai-refined rounded-2xl rounded-tl-sm p-6 text-sm leading-relaxed text-slate-200">
          <p className="font-light tracking-wide text-slate-100">
            Hello! I&apos;m connected to your AgentOS instance. How can I assist
            you today?
          </p>
        </div>
      </motion.div>

      {/* Quick Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="flex flex-wrap justify-center gap-2"
      >
        {QUICK_ACTIONS.map((action) => (
          <button
            key={action.label}
            type="button"
            onClick={() => handleQuickAction(action.prompt)}
            className="flex cursor-pointer items-center gap-2 rounded-lg border border-sky-500/20 bg-sky-500/5 px-4 py-2 text-xs text-sky-300 shadow-[0_0_10px_rgba(56,189,248,0.05)] transition-all hover:border-sky-400/40 hover:bg-sky-500/10 hover:shadow-[0_0_15px_rgba(56,189,248,0.1)]"
          >
            <action.icon className="h-3.5 w-3.5" />
            {action.label}
          </button>
        ))}
      </motion.div>
    </section>
  )
}

export default ChatBlankState
