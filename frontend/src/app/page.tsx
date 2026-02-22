'use client'
import Sidebar from '@/components/chat/Sidebar/Sidebar'
import { ChatArea } from '@/components/chat/ChatArea'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Suspense } from 'react'

export default function Home() {
  // Check if OS_SECURITY_KEY is defined on server-side
  const hasEnvToken = !!process.env.NEXT_PUBLIC_OS_SECURITY_KEY
  const envToken = process.env.NEXT_PUBLIC_OS_SECURITY_KEY || ''
  return (
    <AuthGuard>
      <Suspense fallback={<div>Loading...</div>}>
        <div className="bg-refined-dark flex h-screen overflow-hidden font-sans text-slate-200 antialiased">
          <Sidebar hasEnvToken={hasEnvToken} envToken={envToken} />
          <ChatArea />
        </div>
      </Suspense>
    </AuthGuard>
  )
}
