'use client'

import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import { useHasScope } from '@/auth/useHasScope'
import {
  listMCPVirtualServers,
  createMCPVirtualServer,
  updateMCPVirtualServer,
  toggleMCPVirtualServer,
  deleteMCPVirtualServer,
  listMCPVirtualServerTools,
  listMCPVirtualServerResources,
  listMCPVirtualServerPrompts,
  type MCPVirtualServerInfo,
  type MCPToolInfo,
  type MCPResourceInfo,
  type MCPPromptInfo
} from '@/api/mcp'

interface SubResources {
  tools: MCPToolInfo[]
  resources: MCPResourceInfo[]
  prompts: MCPPromptInfo[]
}

export function VirtualServersTab() {
  const { selectedEndpoint, authToken } = useStore()
  const canWrite = useHasScope('mcp:virtual-servers:write')
  const canDelete = useHasScope('mcp:virtual-servers:delete')

  const [vservers, setVservers] = useState<MCPVirtualServerInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [subResources, setSubResources] = useState<SubResources | null>(null)
  const [actionId, setActionId] = useState<string | null>(null)

  // Form state
  const [formName, setFormName] = useState('')
  const [formDesc, setFormDesc] = useState('')
  const [formVisibility, setFormVisibility] = useState('public')
  const [formTeamId, setFormTeamId] = useState('')

  const fetchData = useCallback(async () => {
    setLoading(true)
    const result = await listMCPVirtualServers(selectedEndpoint, authToken, {
      include_inactive: true
    })
    setVservers(result)
    setLoading(false)
  }, [selectedEndpoint, authToken])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const resetForm = () => {
    setFormName('')
    setFormDesc('')
    setFormVisibility('public')
    setFormTeamId('')
    setShowForm(false)
    setEditingId(null)
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formName.trim()) return
    const result = await createMCPVirtualServer(
      selectedEndpoint,
      {
        name: formName.trim(),
        description: formDesc.trim() || undefined,
        visibility: formVisibility,
        team_id: formTeamId.trim() || undefined
      },
      authToken
    )
    if (result) {
      toast.success(`Created virtual server ${result.name}`)
      resetForm()
      await fetchData()
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingId || !formName.trim()) return
    const result = await updateMCPVirtualServer(
      selectedEndpoint,
      editingId,
      {
        name: formName.trim(),
        description: formDesc.trim() || undefined
      },
      authToken
    )
    if (result) {
      toast.success(`Updated ${result.name}`)
      resetForm()
      await fetchData()
    }
  }

  const startEdit = (vs: MCPVirtualServerInfo) => {
    setEditingId(vs.id)
    setFormName(vs.name)
    setFormDesc(vs.description ?? '')
    setShowForm(false)
  }

  const handleToggle = async (vs: MCPVirtualServerInfo) => {
    setActionId(vs.id)
    const ok = await toggleMCPVirtualServer(
      selectedEndpoint,
      vs.id,
      !vs.is_active,
      authToken
    )
    if (ok) {
      toast.success(`${vs.is_active ? 'Deactivated' : 'Activated'} ${vs.name}`)
      await fetchData()
    }
    setActionId(null)
  }

  const handleDelete = async (vs: MCPVirtualServerInfo) => {
    setActionId(vs.id)
    const ok = await deleteMCPVirtualServer(selectedEndpoint, vs.id, authToken)
    if (ok) {
      toast.success(`Deleted ${vs.name}`)
      await fetchData()
    }
    setActionId(null)
  }

  const handleExpand = async (vs: MCPVirtualServerInfo) => {
    if (expandedId === vs.id) {
      setExpandedId(null)
      setSubResources(null)
      return
    }
    setExpandedId(vs.id)
    const [tools, resources, prompts] = await Promise.all([
      listMCPVirtualServerTools(selectedEndpoint, vs.id, authToken),
      listMCPVirtualServerResources(selectedEndpoint, vs.id, authToken),
      listMCPVirtualServerPrompts(selectedEndpoint, vs.id, authToken)
    ])
    setSubResources({ tools, resources, prompts })
  }

  return (
    <div className="space-y-4">
      {canWrite && !editingId && !showForm && (
        <div>
          <Button variant="outline" size="sm" onClick={() => setShowForm(true)}>
            Add virtual server
          </Button>
        </div>
      )}

      {showForm && canWrite && (
        <form
          onSubmit={handleCreate}
          className="space-y-3 rounded-lg border border-border p-4"
        >
          <div>
            <label htmlFor="vs-name" className="mb-1 block text-xs font-medium">
              Name
            </label>
            <input
              id="vs-name"
              type="text"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="my-virtual-server"
              maxLength={200}
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
              required
            />
          </div>
          <div>
            <label htmlFor="vs-desc" className="mb-1 block text-xs font-medium">
              Description
            </label>
            <input
              id="vs-desc"
              type="text"
              value={formDesc}
              onChange={(e) => setFormDesc(e.target.value)}
              placeholder="Virtual server description"
              maxLength={500}
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
            />
          </div>
          <div>
            <label
              htmlFor="vs-visibility"
              className="mb-1 block text-xs font-medium"
            >
              Visibility
            </label>
            <select
              id="vs-visibility"
              value={formVisibility}
              onChange={(e) => setFormVisibility(e.target.value)}
              className="focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
            >
              <option value="public">Public</option>
              <option value="team">Team</option>
              <option value="private">Private</option>
            </select>
          </div>
          <div>
            <label
              htmlFor="vs-team-id"
              className="mb-1 block text-xs font-medium"
            >
              Team ID (optional)
            </label>
            <input
              id="vs-team-id"
              type="text"
              value={formTeamId}
              onChange={(e) => setFormTeamId(e.target.value)}
              placeholder="team-uuid"
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
            />
          </div>
          <div className="flex gap-2">
            <Button type="submit" size="sm">
              Create
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={resetForm}>
              Cancel
            </Button>
          </div>
        </form>
      )}

      {editingId && canWrite && (
        <form
          onSubmit={handleUpdate}
          className="space-y-3 rounded-lg border border-border p-4"
        >
          <div>
            <label
              htmlFor="vs-edit-name"
              className="mb-1 block text-xs font-medium"
            >
              Name
            </label>
            <input
              id="vs-edit-name"
              type="text"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              maxLength={200}
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
              required
            />
          </div>
          <div>
            <label
              htmlFor="vs-edit-desc"
              className="mb-1 block text-xs font-medium"
            >
              Description
            </label>
            <input
              id="vs-edit-desc"
              type="text"
              value={formDesc}
              onChange={(e) => setFormDesc(e.target.value)}
              maxLength={500}
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
            />
          </div>
          <div className="flex gap-2">
            <Button type="submit" size="sm">
              Save
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={resetForm}>
              Cancel
            </Button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="rounded-lg border border-border p-6">
          <p className="text-muted-foreground text-sm">
            Loading virtual servers&hellip;
          </p>
        </div>
      ) : vservers.length === 0 ? (
        <div className="rounded-lg border border-border p-6">
          <p className="text-muted-foreground text-sm">
            No virtual servers found.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {vservers.map((vs) => (
            <div key={vs.id} className="rounded-lg border border-border p-4">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-block h-2 w-2 rounded-full ${
                        vs.is_active ? 'bg-green-500' : 'bg-muted-foreground'
                      }`}
                    />
                    <h3 className="truncate text-sm font-medium">{vs.name}</h3>
                    {vs.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded bg-muted px-1.5 py-0.5 text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  {vs.description && (
                    <p className="text-muted-foreground mt-1 text-xs">
                      {vs.description}
                    </p>
                  )}
                </div>
                <div className="ml-4 flex shrink-0 gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleExpand(vs)}
                  >
                    {expandedId === vs.id ? 'Collapse' : 'Details'}
                  </Button>
                  {canWrite && (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleToggle(vs)}
                        disabled={actionId === vs.id}
                      >
                        {vs.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => startEdit(vs)}
                      >
                        Edit
                      </Button>
                    </>
                  )}
                  {canDelete && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(vs)}
                      disabled={actionId === vs.id}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      Delete
                    </Button>
                  )}
                </div>
              </div>
              {expandedId === vs.id && subResources && (
                <div className="mt-3 space-y-3 border-t border-border pt-3">
                  <div>
                    <h4 className="mb-1 text-xs font-medium">
                      Tools ({subResources.tools.length})
                    </h4>
                    {subResources.tools.length === 0 ? (
                      <p className="text-muted-foreground text-xs">
                        No tools assigned.
                      </p>
                    ) : (
                      <ul className="space-y-1">
                        {subResources.tools.map((t) => (
                          <li key={t.id} className="text-xs">
                            {t.name}
                            {t.description && (
                              <span className="text-muted-foreground">
                                {' '}
                                &mdash; {t.description}
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div>
                    <h4 className="mb-1 text-xs font-medium">
                      Resources ({subResources.resources.length})
                    </h4>
                    {subResources.resources.length === 0 ? (
                      <p className="text-muted-foreground text-xs">
                        No resources assigned.
                      </p>
                    ) : (
                      <ul className="space-y-1">
                        {subResources.resources.map((r) => (
                          <li key={r.id} className="text-xs">
                            {r.name}
                            {r.uri && (
                              <span className="text-muted-foreground">
                                {' '}
                                ({r.uri})
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div>
                    <h4 className="mb-1 text-xs font-medium">
                      Prompts ({subResources.prompts.length})
                    </h4>
                    {subResources.prompts.length === 0 ? (
                      <p className="text-muted-foreground text-xs">
                        No prompts assigned.
                      </p>
                    ) : (
                      <ul className="space-y-1">
                        {subResources.prompts.map((p) => (
                          <li key={p.id} className="text-xs">
                            {p.name}
                            {p.description && (
                              <span className="text-muted-foreground">
                                {' '}
                                &mdash; {p.description}
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
