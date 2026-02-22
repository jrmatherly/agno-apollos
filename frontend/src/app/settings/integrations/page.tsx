'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { useStore } from '@/store'
import {
  listMCPServers,
  deleteMCPServer,
  registerMCPServer,
  type MCPServerInfo
} from '@/api/mcp'

export default function IntegrationsPage() {
  const { selectedEndpoint, authToken } = useStore()
  const [servers, setServers] = useState<MCPServerInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [newName, setNewName] = useState('')
  const [newUrl, setNewUrl] = useState('')
  const [registering, setRegistering] = useState(false)

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
    setRegistering(true)
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
    setRegistering(false)
  }

  const handleDelete = async (server: MCPServerInfo) => {
    setDeletingId(server.id)
    const ok = await deleteMCPServer(selectedEndpoint, server.id, authToken)
    if (ok) {
      toast.success(`Removed ${server.name}`)
      await fetchServers()
    }
    setDeletingId(null)
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
        <h1 className="mb-2 text-2xl font-semibold">MCP Integrations</h1>
        <p className="text-muted-foreground mb-8 text-sm">
          MCP servers registered through the ContextForge gateway. These servers
          are available to agents for tool discovery and execution.
        </p>

        {showForm ? (
          <form
            onSubmit={handleRegister}
            className="mb-6 space-y-3 rounded-lg border border-border p-4"
          >
            <div>
              <label
                htmlFor="mcp-server-name"
                className="mb-1 block text-xs font-medium"
              >
                Server name
              </label>
              <input
                id="mcp-server-name"
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
                htmlFor="mcp-server-url"
                className="mb-1 block text-xs font-medium"
              >
                Server URL
              </label>
              <input
                id="mcp-server-url"
                type="url"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://mcp-server.example.com/sse"
                className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
                required
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" size="sm" disabled={registering}>
                {registering ? 'Registering...' : 'Register'}
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
          <div className="mb-6">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowForm(true)}
            >
              Add server
            </Button>
          </div>
        )}

        <div className="space-y-3">
          {loading ? (
            <div className="rounded-lg border border-border p-6">
              <p className="text-muted-foreground text-sm">
                Loading integrations&hellip;
              </p>
            </div>
          ) : servers.length === 0 ? (
            <div className="rounded-lg border border-border p-6">
              <p className="text-muted-foreground text-sm">
                No MCP servers registered. Use the &ldquo;Add server&rdquo;
                button above to register one.
              </p>
            </div>
          ) : (
            servers.map((server) => (
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
                  </div>
                  <p className="text-muted-foreground mt-1 truncate text-xs">
                    {server.url}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(server)}
                  disabled={deletingId === server.id}
                  className="text-muted-foreground ml-4 shrink-0 hover:text-destructive"
                >
                  {deletingId === server.id ? 'Removing…' : 'Remove'}
                </Button>
              </div>
            ))
          )}
        </div>

        <div className="mt-6 rounded-lg border border-border bg-muted/50 p-4">
          <p className="text-muted-foreground text-xs">
            <strong>Gateway managed.</strong> MCP servers are routed through
            ContextForge for centralized authentication, audit logging, and
            access control.
          </p>
        </div>
      </div>
    </AuthGuard>
  )
}
