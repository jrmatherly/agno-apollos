'use client'

import Link from 'next/link'
import { AuthGuard } from '@/components/auth/AuthGuard'

export default function SettingsPage() {
  return (
    <AuthGuard>
      <div className="mx-auto max-w-2xl px-6 py-12">
        <Link
          href="/"
          className="text-muted-foreground hover:text-foreground mb-6 inline-block text-sm"
        >
          &larr; Back to Chat
        </Link>
        <h1 className="mb-8 text-2xl font-semibold">Settings</h1>
        <nav className="space-y-2">
          <Link
            href="/settings/m365"
            className="block rounded-lg border border-border p-4 transition-colors hover:bg-muted"
          >
            <h2 className="font-medium">Microsoft 365</h2>
            <p className="text-muted-foreground mt-1 text-sm">
              Connect your Microsoft 365 account to access OneDrive, SharePoint,
              Outlook, Calendar, and Teams.
            </p>
          </Link>
          <Link
            href="/settings/integrations"
            className="block rounded-lg border border-border p-4 transition-colors hover:bg-muted"
          >
            <h2 className="font-medium">MCP Integrations</h2>
            <p className="text-muted-foreground mt-1 text-sm">
              View MCP servers registered through the ContextForge gateway for
              tool discovery and agent access.
            </p>
          </Link>
        </nav>
      </div>
    </AuthGuard>
  )
}
