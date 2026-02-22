'use client'

import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import { useHasScope } from '@/auth/useHasScope'
import {
  listMCPTools,
  createMCPTool,
  updateMCPTool,
  toggleMCPTool,
  deleteMCPTool,
  listMCPServers,
  type MCPToolInfo,
  type MCPServerInfo
} from '@/api/mcp'

export function ToolsTab() {
  const { selectedEndpoint, authToken } = useStore()
  const canWrite = useHasScope('mcp:tools:write')
  const canDelete = useHasScope('mcp:tools:delete')

  const [tools, setTools] = useState<MCPToolInfo[]>([])
  const [servers, setServers] = useState<MCPServerInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [filterGateway, setFilterGateway] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [actionId, setActionId] = useState<string | null>(null)

  // Form state
  const [formName, setFormName] = useState('')
  const [formDesc, setFormDesc] = useState('')
  const [formTags, setFormTags] = useState('')
  const [formVisibility, setFormVisibility] = useState('public')

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [toolsResult, serversResult] = await Promise.all([
      listMCPTools(selectedEndpoint, authToken, {
        gateway_id: filterGateway || undefined,
        include_inactive: true
      }),
      listMCPServers(selectedEndpoint, authToken)
    ])
    setTools(toolsResult)
    setServers(serversResult)
    setLoading(false)
  }, [selectedEndpoint, authToken, filterGateway])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const resetForm = () => {
    setFormName('')
    setFormDesc('')
    setFormTags('')
    setFormVisibility('public')
    setShowForm(false)
    setEditingId(null)
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formName.trim()) return
    const result = await createMCPTool(
      selectedEndpoint,
      {
        name: formName.trim(),
        description: formDesc.trim() || undefined,
        tags: formTags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean),
        visibility: formVisibility
      },
      authToken
    )
    if (result) {
      toast.success(`Created tool ${result.name}`)
      resetForm()
      await fetchData()
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingId || !formName.trim()) return
    const result = await updateMCPTool(
      selectedEndpoint,
      editingId,
      {
        name: formName.trim(),
        description: formDesc.trim() || undefined,
        tags: formTags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean)
      },
      authToken
    )
    if (result) {
      toast.success(`Updated tool ${result.name}`)
      resetForm()
      await fetchData()
    }
  }

  const startEdit = (tool: MCPToolInfo) => {
    setEditingId(tool.id)
    setFormName(tool.name)
    setFormDesc(tool.description ?? '')
    setFormTags(tool.tags.join(', '))
    setShowForm(false)
  }

  const handleToggle = async (tool: MCPToolInfo) => {
    setActionId(tool.id)
    const ok = await toggleMCPTool(
      selectedEndpoint,
      tool.id,
      !tool.is_active,
      authToken
    )
    if (ok) {
      toast.success(
        `${tool.is_active ? 'Deactivated' : 'Activated'} ${tool.name}`
      )
      await fetchData()
    }
    setActionId(null)
  }

  const handleDelete = async (tool: MCPToolInfo) => {
    setActionId(tool.id)
    const ok = await deleteMCPTool(selectedEndpoint, tool.id, authToken)
    if (ok) {
      toast.success(`Deleted ${tool.name}`)
      await fetchData()
    }
    setActionId(null)
  }

  const toolForm = (
    onSubmit: (e: React.FormEvent) => Promise<void>,
    submitLabel: string
  ) => (
    <form
      onSubmit={onSubmit}
      className="space-y-3 rounded-lg border border-border p-4"
    >
      <div>
        <label htmlFor="tool-name" className="mb-1 block text-xs font-medium">
          Name
        </label>
        <input
          id="tool-name"
          type="text"
          value={formName}
          onChange={(e) => setFormName(e.target.value)}
          placeholder="my-tool"
          maxLength={200}
          className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
          required
        />
      </div>
      <div>
        <label htmlFor="tool-desc" className="mb-1 block text-xs font-medium">
          Description
        </label>
        <input
          id="tool-desc"
          type="text"
          value={formDesc}
          onChange={(e) => setFormDesc(e.target.value)}
          placeholder="What this tool does"
          maxLength={500}
          className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
        />
      </div>
      <div>
        <label htmlFor="tool-tags" className="mb-1 block text-xs font-medium">
          Tags (comma-separated)
        </label>
        <input
          id="tool-tags"
          type="text"
          value={formTags}
          onChange={(e) => setFormTags(e.target.value)}
          placeholder="tag1, tag2"
          className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
        />
      </div>
      {!editingId && (
        <div>
          <label
            htmlFor="tool-visibility"
            className="mb-1 block text-xs font-medium"
          >
            Visibility
          </label>
          <select
            id="tool-visibility"
            value={formVisibility}
            onChange={(e) => setFormVisibility(e.target.value)}
            className="focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
          >
            <option value="public">Public</option>
            <option value="team">Team</option>
            <option value="private">Private</option>
          </select>
        </div>
      )}
      <div className="flex gap-2">
        <Button type="submit" size="sm">
          {submitLabel}
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={resetForm}>
          Cancel
        </Button>
      </div>
    </form>
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        {canWrite && !editingId && !showForm && (
          <Button variant="outline" size="sm" onClick={() => setShowForm(true)}>
            Add tool
          </Button>
        )}
        <div className="ml-auto">
          <select
            value={filterGateway}
            onChange={(e) => setFilterGateway(e.target.value)}
            className="focus:ring-ring rounded-md border border-border bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1"
          >
            <option value="">All gateways</option>
            {servers.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {showForm && canWrite && toolForm(handleCreate, 'Create')}
      {editingId && canWrite && toolForm(handleUpdate, 'Save')}

      {loading ? (
        <div className="rounded-lg border border-border p-6">
          <p className="text-muted-foreground text-sm">Loading tools&hellip;</p>
        </div>
      ) : tools.length === 0 ? (
        <div className="rounded-lg border border-border p-6">
          <p className="text-muted-foreground text-sm">No tools found.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {tools.map((tool) => (
            <div key={tool.id} className="rounded-lg border border-border p-4">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-block h-2 w-2 rounded-full ${
                        tool.is_active ? 'bg-green-500' : 'bg-muted-foreground'
                      }`}
                    />
                    <h3 className="truncate text-sm font-medium">
                      {tool.name}
                    </h3>
                    {tool.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded bg-muted px-1.5 py-0.5 text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  {tool.description && (
                    <p className="text-muted-foreground mt-1 text-xs">
                      {tool.description}
                    </p>
                  )}
                </div>
                <div className="ml-4 flex shrink-0 gap-1">
                  {tool.input_schema && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        setExpandedId(expandedId === tool.id ? null : tool.id)
                      }
                    >
                      Schema
                    </Button>
                  )}
                  {canWrite && (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleToggle(tool)}
                        disabled={actionId === tool.id}
                      >
                        {tool.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => startEdit(tool)}
                      >
                        Edit
                      </Button>
                    </>
                  )}
                  {canDelete && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(tool)}
                      disabled={actionId === tool.id}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      Delete
                    </Button>
                  )}
                </div>
              </div>
              {expandedId === tool.id && tool.input_schema && (
                <pre className="mt-3 max-h-48 overflow-auto rounded bg-muted p-3 text-xs">
                  {JSON.stringify(tool.input_schema, null, 2)}
                </pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
