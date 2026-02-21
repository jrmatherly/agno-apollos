'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { useStore } from '@/store'
import {
  connectM365,
  disconnectM365,
  getM365Status,
  type M365Status
} from '@/api/m365'

export default function M365SettingsPage() {
  const { selectedEndpoint, authToken } = useStore()
  const [status, setStatus] = useState<M365Status | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)

  const fetchStatus = useCallback(async () => {
    setLoading(true)
    const result = await getM365Status(selectedEndpoint, authToken)
    setStatus(result)
    setLoading(false)
  }, [selectedEndpoint, authToken])

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  const handleConnect = async () => {
    setActionLoading(true)
    const result = await connectM365(selectedEndpoint, authToken)
    if (result.connected) {
      toast.success('Microsoft 365 connected successfully')
    }
    await fetchStatus()
    setActionLoading(false)
  }

  const handleDisconnect = async () => {
    setActionLoading(true)
    await disconnectM365(selectedEndpoint, authToken)
    toast.success('Microsoft 365 disconnected')
    await fetchStatus()
    setActionLoading(false)
  }

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

        <div className="rounded-lg border border-border p-6">
          {loading ? (
            <p className="text-muted-foreground text-sm">
              Checking connection status&hellip;
            </p>
          ) : status?.connected ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <span className="inline-block h-2 w-2 rounded-full bg-green-500" />
                <span className="text-sm font-medium">Connected</span>
                {status.account && (
                  <span className="text-muted-foreground text-xs">
                    ({status.account})
                  </span>
                )}
              </div>
              {status.scopes && status.scopes.length > 0 && (
                <div>
                  <p className="text-muted-foreground mb-1 text-xs font-medium">
                    Granted scopes
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {status.scopes.map((scope) => (
                      <span
                        key={scope}
                        className="rounded bg-muted px-2 py-0.5 text-xs"
                      >
                        {scope}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <Button
                variant="outline"
                onClick={handleDisconnect}
                disabled={actionLoading}
              >
                {actionLoading ? 'Disconnecting…' : 'Disconnect'}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <span className="bg-muted-foreground inline-block h-2 w-2 rounded-full" />
                <span className="text-sm font-medium">Not connected</span>
              </div>
              {status?.needs_reconnect ? (
                <p className="text-muted-foreground text-sm">
                  Your previous session expired. Reconnect to restore access.
                </p>
              ) : (
                <p className="text-muted-foreground text-sm">
                  Connecting grants read-only access to your Microsoft 365
                  resources. No data will be modified.
                </p>
              )}
              <Button onClick={handleConnect} disabled={actionLoading}>
                {actionLoading ? 'Connecting…' : 'Connect Microsoft 365'}
              </Button>
            </div>
          )}
        </div>

        <div className="mt-6 rounded-lg border border-border bg-muted/50 p-4">
          <p className="text-muted-foreground text-xs">
            <strong>Read-only access.</strong> This integration can only read
            your data — it cannot send emails, create files, modify calendar
            events, or perform any write operations.
          </p>
        </div>
      </div>
    </AuthGuard>
  )
}
