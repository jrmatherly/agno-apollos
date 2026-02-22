import { Bot, Copy, ThumbsUp, ThumbsDown } from 'lucide-react'
import MarkdownRenderer from '@/components/ui/typography/MarkdownRenderer'
import { useStore } from '@/store'
import type { ChatMessage } from '@/types/os'
import Videos from './Multimedia/Videos'
import Images from './Multimedia/Images'
import Audios from './Multimedia/Audios'
import { memo } from 'react'
import AgentThinkingLoader from './AgentThinkingLoader'
import { isMsalConfigured, useAuth } from '@/auth'
import { getInitials } from '@/lib/utils'

interface MessageProps {
  message: ChatMessage
}

const AgentMessage = ({ message }: MessageProps) => {
  const { streamingErrorMessage } = useStore()
  let messageContent
  if (message.streamingError) {
    messageContent = (
      <p className="text-destructive">
        Oops! Something went wrong while streaming.{' '}
        {streamingErrorMessage ? (
          <>{streamingErrorMessage}</>
        ) : (
          'Please try refreshing the page or try again later.'
        )}
      </p>
    )
  } else if (message.content) {
    messageContent = (
      <div className="flex w-full flex-col gap-4">
        <MarkdownRenderer>{message.content}</MarkdownRenderer>
        {message.videos && message.videos.length > 0 && (
          <Videos videos={message.videos} />
        )}
        {message.images && message.images.length > 0 && (
          <Images images={message.images} />
        )}
        {message.audio && message.audio.length > 0 && (
          <Audios audio={message.audio} />
        )}
      </div>
    )
  } else if (message.response_audio) {
    if (!message.response_audio.transcript) {
      messageContent = (
        <div className="mt-2 flex items-start">
          <AgentThinkingLoader />
        </div>
      )
    } else {
      messageContent = (
        <div className="flex w-full flex-col gap-4">
          <MarkdownRenderer>
            {message.response_audio.transcript}
          </MarkdownRenderer>
          {message.response_audio.content && message.response_audio && (
            <Audios audio={[message.response_audio]} />
          )}
        </div>
      )
    }
  } else {
    messageContent = (
      <div className="mt-2">
        <AgentThinkingLoader />
      </div>
    )
  }

  return (
    <div className="group flex max-w-3xl items-start gap-4 font-sans">
      <div className="mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl border border-sky-500/20 bg-gradient-to-br from-sky-900/30 to-slate-900/50 shadow-[0_0_15px_rgba(56,189,248,0.15)]">
        <Bot className="h-5 w-5 text-sky-400 opacity-90" />
      </div>
      <div className="flex flex-col gap-2">
        <div className="glass-bubble-ai-refined rounded-2xl rounded-tl-sm p-6 text-sm leading-relaxed text-slate-200">
          {messageContent}
        </div>
        <div className="flex items-center gap-2 px-2 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
          <button
            className="cursor-pointer rounded-lg p-1.5 text-slate-500 transition-colors hover:bg-white/5 hover:text-sky-400"
            title="Copy to clipboard"
          >
            <Copy className="h-3.5 w-3.5" />
          </button>
          <button
            className="cursor-pointer rounded-lg p-1.5 text-slate-500 transition-colors hover:bg-white/5 hover:text-emerald-400"
            title="Helpful"
          >
            <ThumbsUp className="h-3.5 w-3.5" />
          </button>
          <button
            className="cursor-pointer rounded-lg p-1.5 text-slate-500 transition-colors hover:bg-white/5 hover:text-red-400"
            title="Not helpful"
          >
            <ThumbsDown className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}

function MsalUserAvatar() {
  const { account } = useAuth()
  const initials = account?.name ? getInitials(account.name) : 'U'
  return (
    <div className="mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full border border-white/10 bg-gradient-to-br from-slate-700 to-slate-800 text-xs font-medium text-white shadow-md">
      {initials}
    </div>
  )
}

function DefaultUserAvatar() {
  return (
    <div className="mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full border border-white/10 bg-slate-700 text-xs text-white shadow-md">
      U
    </div>
  )
}

const UserMessage = memo(({ message }: MessageProps) => {
  return (
    <div className="ml-auto flex max-w-3xl flex-row-reverse items-start gap-4 font-sans">
      {isMsalConfigured ? <MsalUserAvatar /> : <DefaultUserAvatar />}
      <div className="glass-bubble-user-refined rounded-2xl rounded-tr-sm p-4 px-5 text-sm font-light leading-relaxed text-slate-200">
        {message.content}
      </div>
    </div>
  )
})

AgentMessage.displayName = 'AgentMessage'
UserMessage.displayName = 'UserMessage'
export { AgentMessage, UserMessage }
