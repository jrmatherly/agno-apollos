'use client'

import Link from 'next/link'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { M365SettingsContent } from './M365SettingsContent'

export default function M365SettingsPage() {
  return (
    <AuthGuard>
      <div className="mx-auto max-w-2xl px-6 py-12">
        <Link
          href="/settings"
          className="text-muted-foreground hover:text-foreground mb-6 inline-block text-sm"
        >
          &larr; Settings
        </Link>
        <h1 className="mb-2 text-2xl font-semibold">Microsoft 365</h1>
        <p className="text-muted-foreground mb-8 text-sm">
          Connect your Microsoft 365 account to access OneDrive, SharePoint,
          Outlook email, Calendar, and Teams messages.
        </p>
        <M365SettingsContent />
      </div>
    </AuthGuard>
  )
}
