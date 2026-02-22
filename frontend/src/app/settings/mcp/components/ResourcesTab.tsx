'use client'

import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import { useHasScope } from '@/auth/useHasScope'
import {
  listMCPResources,
  createMCPResource,
  updateMCPResource,
  toggleMCPResource,
  deleteMCPResource,
  type MCPResourceInfo
} from '@/api/mcp'

export function ResourcesTab() {
  const { selectedEndpoint, authToken } = useStore()
  const canWrite = useHasScope('mcp:resources:write')
  const canDelete = useHasScope('mcp:resources:delete')

  const [resources, setResources] = useState<MCPResourceInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [actionId, setActionId] = useState<string | null>(null)

  // Form state
  const [formName, setFormName] = useState('')
  const [formUri, setFormUri] = useState('')
  const [formDesc, setFormDesc] = useState('')
  const [formMime, setFormMime] = useState('')
  const [formVisibility, setFormVisibility] = useState('public')
  const [formTeamId, setFormTeamId] = useState('')

  const fetchData = useCallback(async () => {
    setLoading(true)
    const result = await listMCPResources(selectedEndpoint, authToken, {
      include_inactive: true
    })
    setResources(result)
    setLoading(false)
  }, [selectedEndpoint, authToken])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const resetForm = () => {
    setFormName('')
    setFormUri('')
    setFormDesc('')
    setFormMime('')
    setFormVisibility('public')
    setFormTeamId('')
    setShowForm(false)
    setEditingId(null)
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formName.trim()) return
    const result = await createMCPResource(
      selectedEndpoint,
      {
        name: formName.trim(),
        uri: formUri.trim() || undefined,
        description: formDesc.trim() || undefined,
        mime_type: formMime.trim() || undefined,
        visibility: formVisibility,
        team_id: formTeamId.trim() || undefined
      },
      authToken
    )
    if (result) {
      toast.success(`Created resource ${result.name}`)
      resetForm()
      await fetchData()
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingId || !formName.trim()) return
    const result = await updateMCPResource(
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

  const startEdit = (resource: MCPResourceInfo) => {
    setEditingId(resource.id)
    setFormName(resource.name)
    setFormDesc(resource.description ?? '')
    setShowForm(false)
  }

  const handleToggle = async (resource: MCPResourceInfo) => {
    setActionId(resource.id)
    const ok = await toggleMCPResource(
      selectedEndpoint,
      resource.id,
      !resource.is_active,
      authToken
    )
    if (ok) {
      toast.success(
        `${resource.is_active ? 'Deactivated' : 'Activated'} ${resource.name}`
      )
      await fetchData()
    }
    setActionId(null)
  }

  const handleDelete = async (resource: MCPResourceInfo) => {
    setActionId(resource.id)
    const ok = await deleteMCPResource(selectedEndpoint, resource.id, authToken)
    if (ok) {
      toast.success(`Deleted ${resource.name}`)
      await fetchData()
    }
    setActionId(null)
  }

  return (
    <div className="space-y-4">
      {canWrite && !editingId && !showForm && (
        <div>
          <Button variant="outline" size="sm" onClick={() => setShowForm(true)}>
            Add resource
          </Button>
        </div>
      )}

      {showForm && canWrite && (
        <form
          onSubmit={handleCreate}
          className="space-y-3 rounded-lg border border-border p-4"
        >
          <div>
            <label
              htmlFor="res-name"
              className="mb-1 block text-xs font-medium"
            >
              Name
            </label>
            <input
              id="res-name"
              type="text"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="my-resource"
              maxLength={200}
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
              required
            />
          </div>
          <div>
            <label htmlFor="res-uri" className="mb-1 block text-xs font-medium">
              URI
            </label>
            <input
              id="res-uri"
              type="text"
              value={formUri}
              onChange={(e) => setFormUri(e.target.value)}
              placeholder="file:///data/config.json"
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
            />
          </div>
          <div>
            <label
              htmlFor="res-desc"
              className="mb-1 block text-xs font-medium"
            >
              Description
            </label>
            <input
              id="res-desc"
              type="text"
              value={formDesc}
              onChange={(e) => setFormDesc(e.target.value)}
              placeholder="Resource description"
              maxLength={500}
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
            />
          </div>
          <div>
            <label
              htmlFor="res-mime"
              className="mb-1 block text-xs font-medium"
            >
              MIME type
            </label>
            <input
              id="res-mime"
              type="text"
              value={formMime}
              onChange={(e) => setFormMime(e.target.value)}
              placeholder="application/json"
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
            />
          </div>
          <div>
            <label
              htmlFor="res-visibility"
              className="mb-1 block text-xs font-medium"
            >
              Visibility
            </label>
            <select
              id="res-visibility"
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
              htmlFor="res-team-id"
              className="mb-1 block text-xs font-medium"
            >
              Team ID (optional)
            </label>
            <input
              id="res-team-id"
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
              htmlFor="res-edit-name"
              className="mb-1 block text-xs font-medium"
            >
              Name
            </label>
            <input
              id="res-edit-name"
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
              htmlFor="res-edit-desc"
              className="mb-1 block text-xs font-medium"
            >
              Description
            </label>
            <input
              id="res-edit-desc"
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
            Loading resources&hellip;
          </p>
        </div>
      ) : resources.length === 0 ? (
        <div className="rounded-lg border border-border p-6">
          <p className="text-muted-foreground text-sm">No resources found.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {resources.map((resource) => (
            <div
              key={resource.id}
              className="flex items-center justify-between rounded-lg border border-border p-4"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-block h-2 w-2 rounded-full ${
                      resource.is_active
                        ? 'bg-green-500'
                        : 'bg-muted-foreground'
                    }`}
                  />
                  <h3 className="truncate text-sm font-medium">
                    {resource.name}
                  </h3>
                  {resource.mime_type && (
                    <span className="rounded bg-muted px-1.5 py-0.5 text-xs">
                      {resource.mime_type}
                    </span>
                  )}
                </div>
                {resource.uri && (
                  <p className="text-muted-foreground mt-1 truncate text-xs">
                    {resource.uri}
                  </p>
                )}
                {resource.description && (
                  <p className="text-muted-foreground mt-0.5 text-xs">
                    {resource.description}
                  </p>
                )}
              </div>
              <div className="ml-4 flex shrink-0 gap-1">
                {canWrite && (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggle(resource)}
                      disabled={actionId === resource.id}
                    >
                      {resource.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => startEdit(resource)}
                    >
                      Edit
                    </Button>
                  </>
                )}
                {canDelete && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(resource)}
                    disabled={actionId === resource.id}
                    className="text-muted-foreground hover:text-destructive"
                  >
                    Delete
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
