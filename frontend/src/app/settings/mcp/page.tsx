'use client'

import Link from 'next/link'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { MCPSettingsContent } from './MCPSettingsContent'

export default function MCPSettingsPage() {
  return (
    <AuthGuard>
      <div className="mx-auto max-w-4xl px-6 py-12">
        <Link
          href="/settings"
          className="text-muted-foreground hover:text-foreground mb-6 inline-block text-sm"
        >
          &larr; Settings
        </Link>
        <h1 className="mb-2 text-2xl font-semibold">MCP Gateway</h1>
        <p className="text-muted-foreground mb-8 text-sm">
          Manage MCP servers, tools, virtual servers, resources, and prompts
          through the ContextForge gateway.
        </p>
        <MCPSettingsContent />
      </div>
    </AuthGuard>
  )
}
