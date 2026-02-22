'use client'

import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import { useHasScope } from '@/auth/useHasScope'
import {
  listMCPServers,
  registerMCPServer,
  deleteMCPServer,
  toggleMCPServer,
  refreshMCPServer,
  type MCPServerInfo
} from '@/api/mcp'

export function ServersTab() {
  const { selectedEndpoint, authToken } = useStore()
  const canWrite = useHasScope('mcp:servers:write')
  const canDelete = useHasScope('mcp:servers:delete')

  const [servers, setServers] = useState<MCPServerInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newName, setNewName] = useState('')
  const [newUrl, setNewUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [actionId, setActionId] = useState<string | null>(null)

  const fetchServers = useCallback(async () => {
    setLoading(true)
    const result = await listMCPServers(selectedEndpoint, authToken)
    setServers(result)
    setLoading(false)
  }, [selectedEndpoint, authToken])

  useEffect(() => {
    fetchServers()
  }, [fetchServers])

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newName.trim() || !newUrl.trim()) return
    setSubmitting(true)
    const result = await registerMCPServer(
      selectedEndpoint,
      newName.trim(),
      newUrl.trim(),
      authToken
    )
    if (result) {
      toast.success(`Registered ${result.name}`)
      setNewName('')
      setNewUrl('')
      setShowForm(false)
      await fetchServers()
    }
    setSubmitting(false)
  }

  const handleDelete = async (server: MCPServerInfo) => {
    setActionId(server.id)
    const ok = await deleteMCPServer(selectedEndpoint, server.id, authToken)
    if (ok) {
      toast.success(`Removed ${server.name}`)
      await fetchServers()
    }
    setActionId(null)
  }

  const handleToggle = async (server: MCPServerInfo) => {
    const activate = server.status !== 'active'
    setActionId(server.id)
    const ok = await toggleMCPServer(
      selectedEndpoint,
      server.id,
      activate,
      authToken
    )
    if (ok) {
      toast.success(`${activate ? 'Activated' : 'Deactivated'} ${server.name}`)
      await fetchServers()
    }
    setActionId(null)
  }

  const handleRefresh = async (server: MCPServerInfo) => {
    setActionId(server.id)
    const result = await refreshMCPServer(
      selectedEndpoint,
      server.id,
      authToken
    )
    if (result) {
      toast.success(`Refreshed ${server.name}`)
    }
    setActionId(null)
  }

  return (
    <div className="space-y-4">
      {canWrite &&
        (showForm ? (
          <form
            onSubmit={handleRegister}
            className="space-y-3 rounded-lg border border-border p-4"
          >
            <div>
              <label
                htmlFor="server-name"
                className="mb-1 block text-xs font-medium"
              >
                Server name
              </label>
              <input
                id="server-name"
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="my-mcp-server"
                pattern="^[a-z0-9][a-z0-9_-]*$"
                title="Lowercase letters, numbers, hyphens, and underscores. Must start with a letter or number."
                maxLength={100}
                className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
                required
              />
            </div>
            <div>
              <label
                htmlFor="server-url"
                className="mb-1 block text-xs font-medium"
              >
                Server URL
              </label>
              <input
                id="server-url"
                type="url"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://mcp-server.example.com/sse"
                className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
                required
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" size="sm" disabled={submitting}>
                {submitting ? 'Registering\u2026' : 'Register'}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowForm(false)
                  setNewName('')
                  setNewUrl('')
                }}
              >
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowForm(true)}
            >
              Add server
            </Button>
          </div>
        ))}

      {loading ? (
        <div className="rounded-lg border border-border p-6">
          <p className="text-muted-foreground text-sm">
            Loading servers&hellip;
          </p>
        </div>
      ) : servers.length === 0 ? (
        <div className="rounded-lg border border-border p-6">
          <p className="text-muted-foreground text-sm">
            No MCP servers registered.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {servers.map((server) => (
            <div
              key={server.id}
              className="flex items-center justify-between rounded-lg border border-border p-4"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-block h-2 w-2 rounded-full ${
                      server.status === 'active'
                        ? 'bg-green-500'
                        : 'bg-muted-foreground'
                    }`}
                  />
                  <h3 className="truncate text-sm font-medium">
                    {server.name}
                  </h3>
                  <span className="rounded bg-muted px-1.5 py-0.5 text-xs">
                    {server.status ?? 'unknown'}
                  </span>
                </div>
                <p className="text-muted-foreground mt-1 truncate text-xs">
                  {server.url}
                </p>
              </div>
              <div className="ml-4 flex shrink-0 gap-1">
                {canWrite && (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggle(server)}
                      disabled={actionId === server.id}
                    >
                      {server.status === 'active' ? 'Deactivate' : 'Activate'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRefresh(server)}
                      disabled={actionId === server.id}
                    >
                      Refresh
                    </Button>
                  </>
                )}
                {canDelete && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(server)}
                    disabled={actionId === server.id}
                    className="text-muted-foreground hover:text-destructive"
                  >
                    Remove
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
