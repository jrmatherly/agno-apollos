'use client'
import { Button } from '@/components/ui/button'
import useChatActions from '@/hooks/useChatActions'
import { useStore } from '@/store'
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import Icon from '@/components/ui/icon'
import Sessions from './Sessions'
import AuthToken from './AuthToken'
import { isMsalConfigured } from '@/auth'
import { UserMenu } from './UserMenu'
import Image from 'next/image'
const SidebarHeader = () => (
  <div className="flex items-center gap-3 px-2 pt-2">
    <div className="relative flex h-10 w-10 items-center justify-center">
      <div className="absolute inset-0 rounded-full bg-blue-500/20 blur-md" />
      <Image
        src="/apollos_round_no_bg.svg"
        alt="Apollos AI"
        width={32}
        height={32}
        className="relative z-10"
      />
    </div>
    <span className="bg-gradient-to-br from-white via-slate-200 to-slate-400 bg-clip-text font-heading text-lg font-semibold tracking-wide text-transparent">
      Apollos AI
    </span>
  </div>
)

const NewChatButton = ({
  disabled,
  onClick
}: {
  disabled: boolean
  onClick: () => void
}) => (
  <Button
    onClick={onClick}
    disabled={disabled}
    size="lg"
    className="metallic-border group relative h-11 w-full overflow-hidden rounded-xl bg-gradient-to-b from-white/5 to-white/0 text-sm font-medium tracking-wide text-slate-200 shadow-lg shadow-black/20 transition-all duration-300 hover:border-blue-400/30 hover:from-white/10 hover:to-white/5"
  >
    <div className="absolute inset-0 translate-x-[-100%] transform bg-gradient-to-r from-brand/0 via-brand/5 to-brand/0 opacity-0 transition-opacity duration-500 group-hover:translate-x-[100%] group-hover:opacity-100" />
    <Icon type="plus-icon" size="xs" className="mr-2 text-sky-400" />
    <span>New Chat</span>
  </Button>
)

const Sidebar = ({
  hasEnvToken,
  envToken
}: {
  hasEnvToken?: boolean
  envToken?: string
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { clearChat, focusChatInput, initialize } = useChatActions()
  const { messages, selectedEndpoint, isEndpointActive, hydrated, authToken } =
    useStore()
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
    // When MSAL is configured, wait for the token to be synced before initializing.
    // Calling initialize() with an empty token sends unauthenticated requests that
    // return 401, causing spurious toast errors before the token is ready.
    if (hydrated && (!isMsalConfigured || authToken)) initialize()
  }, [selectedEndpoint, initialize, hydrated, authToken])

  const handleNewChat = () => {
    clearChat()
    focusChatInput()
  }

  return (
    <motion.aside
      className="sidebar-glass-premium relative flex h-screen shrink-0 grow-0 flex-col overflow-hidden font-sans"
      initial={{ width: '16rem' }}
      animate={{ width: isCollapsed ? '2.5rem' : '16rem' }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <motion.button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute right-2 top-2 z-10 p-1"
        aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        type="button"
        whileTap={{ scale: 0.95 }}
      >
        <Icon
          type="sheet"
          size="xs"
          className={`transform ${isCollapsed ? 'rotate-180' : 'rotate-0'}`}
        />
      </motion.button>
      <motion.div
        className="flex w-60 flex-1 flex-col gap-5 p-4"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: isCollapsed ? 0 : 1, x: isCollapsed ? -20 : 0 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        style={{
          pointerEvents: isCollapsed ? 'none' : 'auto'
        }}
      >
        <SidebarHeader />
        <NewChatButton
          disabled={messages.length === 0}
          onClick={handleNewChat}
        />
        {isMounted && (
          <>
            {isEndpointActive && <Sessions />}
            {!isMsalConfigured && (
              <AuthToken hasEnvToken={hasEnvToken} envToken={envToken} />
            )}
          </>
        )}

        <div className="mt-auto">
          <UserMenu />
        </div>
      </motion.div>
    </motion.aside>
  )
}

export default Sidebar
