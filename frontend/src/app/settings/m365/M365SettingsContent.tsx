'use client'

import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import {
  connectM365,
  disconnectM365,
  getM365Status,
  type M365Status
} from '@/api/m365'

export function M365SettingsContent() {
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
    <div className="space-y-6">
      <div className="rounded-lg border border-white/10 p-6">
        {loading ? (
          <p className="text-sm text-slate-400">
            Checking connection status&hellip;
          </p>
        ) : status?.connected ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="inline-block h-2 w-2 rounded-full bg-green-500" />
              <span className="text-sm font-medium text-slate-200">
                Connected
              </span>
              {status.account && (
                <span className="text-xs text-slate-400">
                  ({status.account})
                </span>
              )}
            </div>
            {status.scopes && status.scopes.length > 0 && (
              <div>
                <p className="mb-1 text-xs font-medium text-slate-400">
                  Granted scopes
                </p>
                <div className="flex flex-wrap gap-1">
                  {status.scopes.map((scope) => (
                    <span
                      key={scope}
                      className="rounded bg-white/5 px-2 py-0.5 text-xs text-slate-300"
                    >
                      {scope}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <Button
              variant="outline"
              className="border-white/10"
              onClick={handleDisconnect}
              disabled={actionLoading}
            >
              {actionLoading ? 'Disconnecting\u2026' : 'Disconnect'}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="inline-block h-2 w-2 rounded-full bg-slate-500" />
              <span className="text-sm font-medium text-slate-200">
                Not connected
              </span>
            </div>
            {status?.needs_reconnect ? (
              <p className="text-sm text-slate-400">
                Your previous session expired. Reconnect to restore access.
              </p>
            ) : (
              <p className="text-sm text-slate-400">
                Connecting grants read-only access to your Microsoft 365
                resources. No data will be modified.
              </p>
            )}
            <Button
              className="bg-sky-500 text-white hover:bg-sky-400"
              onClick={handleConnect}
              disabled={actionLoading}
            >
              {actionLoading ? 'Connecting\u2026' : 'Connect Microsoft 365'}
            </Button>
          </div>
        )}
      </div>

      <div className="rounded-lg border border-white/5 bg-white/[0.02] p-4">
        <p className="text-xs text-slate-400">
          <strong className="text-slate-300">Read-only access.</strong> This
          integration can only read your data — it cannot send emails, create
          files, modify calendar events, or perform any write operations.
        </p>
      </div>
    </div>
  )
}
