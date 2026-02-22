'use client'

import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import { useHasScope } from '@/auth/useHasScope'
import {
  listMCPPrompts,
  createMCPPrompt,
  updateMCPPrompt,
  toggleMCPPrompt,
  deleteMCPPrompt,
  type MCPPromptInfo
} from '@/api/mcp'

export function PromptsTab() {
  const { selectedEndpoint, authToken } = useStore()
  const canWrite = useHasScope('mcp:prompts:write')
  const canDelete = useHasScope('mcp:prompts:delete')

  const [prompts, setPrompts] = useState<MCPPromptInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [actionId, setActionId] = useState<string | null>(null)

  // Form state
  const [formName, setFormName] = useState('')
  const [formDesc, setFormDesc] = useState('')
  const [formVisibility, setFormVisibility] = useState('public')
  const [formTeamId, setFormTeamId] = useState('')

  const fetchData = useCallback(async () => {
    setLoading(true)
    const result = await listMCPPrompts(selectedEndpoint, authToken, {
      include_inactive: true
    })
    setPrompts(result)
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
    const result = await createMCPPrompt(
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
      toast.success(`Created prompt ${result.name}`)
      resetForm()
      await fetchData()
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingId || !formName.trim()) return
    const result = await updateMCPPrompt(
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

  const startEdit = (prompt: MCPPromptInfo) => {
    setEditingId(prompt.id)
    setFormName(prompt.name)
    setFormDesc(prompt.description ?? '')
    setShowForm(false)
  }

  const handleToggle = async (prompt: MCPPromptInfo) => {
    setActionId(prompt.id)
    const ok = await toggleMCPPrompt(
      selectedEndpoint,
      prompt.id,
      !prompt.is_active,
      authToken
    )
    if (ok) {
      toast.success(
        `${prompt.is_active ? 'Deactivated' : 'Activated'} ${prompt.name}`
      )
      await fetchData()
    }
    setActionId(null)
  }

  const handleDelete = async (prompt: MCPPromptInfo) => {
    setActionId(prompt.id)
    const ok = await deleteMCPPrompt(selectedEndpoint, prompt.id, authToken)
    if (ok) {
      toast.success(`Deleted ${prompt.name}`)
      await fetchData()
    }
    setActionId(null)
  }

  return (
    <div className="space-y-4">
      {canWrite && !editingId && !showForm && (
        <div>
          <Button variant="outline" size="sm" onClick={() => setShowForm(true)}>
            Add prompt
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
              htmlFor="prompt-name"
              className="mb-1 block text-xs font-medium"
            >
              Name
            </label>
            <input
              id="prompt-name"
              type="text"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="my-prompt"
              maxLength={200}
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
              required
            />
          </div>
          <div>
            <label
              htmlFor="prompt-desc"
              className="mb-1 block text-xs font-medium"
            >
              Description
            </label>
            <input
              id="prompt-desc"
              type="text"
              value={formDesc}
              onChange={(e) => setFormDesc(e.target.value)}
              placeholder="What this prompt does"
              maxLength={500}
              className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
            />
          </div>
          <div>
            <label
              htmlFor="prompt-visibility"
              className="mb-1 block text-xs font-medium"
            >
              Visibility
            </label>
            <select
              id="prompt-visibility"
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
              htmlFor="prompt-team-id"
              className="mb-1 block text-xs font-medium"
            >
              Team ID (optional)
            </label>
            <input
              id="prompt-team-id"
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
              htmlFor="prompt-edit-name"
              className="mb-1 block text-xs font-medium"
            >
              Name
            </label>
            <input
              id="prompt-edit-name"
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
              htmlFor="prompt-edit-desc"
              className="mb-1 block text-xs font-medium"
            >
              Description
            </label>
            <input
              id="prompt-edit-desc"
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
            Loading prompts&hellip;
          </p>
        </div>
      ) : prompts.length === 0 ? (
        <div className="rounded-lg border border-border p-6">
          <p className="text-muted-foreground text-sm">No prompts found.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {prompts.map((prompt) => (
            <div
              key={prompt.id}
              className="rounded-lg border border-border p-4"
            >
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-block h-2 w-2 rounded-full ${
                        prompt.is_active
                          ? 'bg-green-500'
                          : 'bg-muted-foreground'
                      }`}
                    />
                    <h3 className="truncate text-sm font-medium">
                      {prompt.name}
                    </h3>
                  </div>
                  {prompt.description && (
                    <p className="text-muted-foreground mt-1 text-xs">
                      {prompt.description}
                    </p>
                  )}
                </div>
                <div className="ml-4 flex shrink-0 gap-1">
                  {canWrite && (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleToggle(prompt)}
                        disabled={actionId === prompt.id}
                      >
                        {prompt.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => startEdit(prompt)}
                      >
                        Edit
                      </Button>
                    </>
                  )}
                  {canDelete && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(prompt)}
                      disabled={actionId === prompt.id}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      Delete
                    </Button>
                  )}
                </div>
              </div>
              {prompt.arguments.length > 0 && (
                <div className="mt-2 border-t border-border pt-2">
                  <p className="mb-1 text-xs font-medium">Arguments</p>
                  <ul className="space-y-0.5">
                    {prompt.arguments.map((arg) => (
                      <li
                        key={arg.name}
                        className="flex items-center gap-2 text-xs"
                      >
                        <code className="rounded bg-muted px-1 py-0.5">
                          {arg.name}
                        </code>
                        {arg.required && (
                          <span className="text-destructive">required</span>
                        )}
                        {arg.description && (
                          <span className="text-muted-foreground">
                            &mdash; {arg.description}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
