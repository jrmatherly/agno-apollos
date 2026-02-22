'use client'
import { useState } from 'react'
import { toast } from 'sonner'
import { TextArea } from '@/components/ui/textarea'
import { useStore } from '@/store'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { PlusCircle, Mic, ArrowUp } from 'lucide-react'

const ChatInput = () => {
  const { chatInputRef } = useStore()

  const { handleStreamResponse } = useAIChatStreamHandler()
  const [inputMessage, setInputMessage] = useState('')
  const isStreaming = useStore((state) => state.isStreaming)
  const handleSubmit = async () => {
    if (!inputMessage.trim()) return

    const currentMessage = inputMessage
    setInputMessage('')

    try {
      await handleStreamResponse(currentMessage)
    } catch (error) {
      toast.error(
        `Error in handleSubmit: ${
          error instanceof Error ? error.message : String(error)
        }`
      )
    }
  }

  return (
    <div className="relative font-sans">
      <div className="relative flex items-end rounded-2xl border border-white/10 bg-background/80 p-2 shadow-2xl backdrop-blur-2xl transition-all focus-within:border-brand/50 focus-within:bg-background/90 focus-within:ring-1 focus-within:ring-sky-500/20">
        <div className="flex h-[44px] items-center px-2">
          <button
            type="button"
            className="rounded-xl p-2 text-slate-500 transition-colors"
            title="Attach context"
            disabled
          >
            <PlusCircle className="h-5 w-5" />
          </button>
        </div>

        <div className="min-w-0 flex-1 py-3">
          <TextArea
            placeholder="Ask anything..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (
                e.key === 'Enter' &&
                !e.nativeEvent.isComposing &&
                !e.shiftKey &&
                !isStreaming
              ) {
                e.preventDefault()
                handleSubmit()
              }
            }}
            className="w-full bg-transparent font-heading font-light tracking-wide text-white placeholder-slate-500"
            disabled={false}
            ref={chatInputRef}
          />
        </div>

        <div className="flex h-[44px] items-center gap-2 px-2">
          <button
            type="button"
            className="rounded-xl p-2 text-slate-500 transition-colors"
            disabled
          >
            <Mic className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!inputMessage.trim() || isStreaming}
            className="group flex h-10 w-10 transform cursor-pointer items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 to-blue-600 text-white shadow-[0_0_20px_rgba(56,189,248,0.3)] transition-all hover:shadow-[0_0_30px_rgba(56,189,248,0.5)] active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <ArrowUp className="h-5 w-5 font-bold transition-transform group-hover:-translate-y-0.5" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInput
