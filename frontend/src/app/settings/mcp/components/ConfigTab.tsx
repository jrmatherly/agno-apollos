'use client'

import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import { useHasScope } from '@/auth/useHasScope'
import {
  getMCPHealth,
  exportMCPConfig,
  importMCPConfig,
  listMCPTags,
  type MCPHealthInfo,
  type MCPTagInfo,
  type MCPImportResult
} from '@/api/mcp'

export function ConfigTab() {
  const { selectedEndpoint, authToken } = useStore()
  const canConfigWrite = useHasScope('mcp:config:write')

  const [health, setHealth] = useState<MCPHealthInfo | null>(null)
  const [tags, setTags] = useState<MCPTagInfo[]>([])
  const [healthLoading, setHealthLoading] = useState(true)

  // Export state
  const [exportTypes, setExportTypes] = useState('')
  const [exportTags, setExportTags] = useState('')
  const [exportInactive, setExportInactive] = useState(false)
  const [exporting, setExporting] = useState(false)

  // Import state
  const [importFile, setImportFile] = useState<File | null>(null)
  const [conflictStrategy, setConflictStrategy] = useState('update')
  const [dryRun, setDryRun] = useState(false)
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<MCPImportResult | null>(null)

  const fetchHealth = useCallback(async () => {
    setHealthLoading(true)
    const [h, t] = await Promise.all([
      getMCPHealth(selectedEndpoint, authToken),
      listMCPTags(selectedEndpoint, authToken)
    ])
    setHealth(h)
    setTags(t)
    setHealthLoading(false)
  }, [selectedEndpoint, authToken])

  useEffect(() => {
    fetchHealth()
  }, [fetchHealth])

  const handleExport = async () => {
    setExporting(true)
    const data = await exportMCPConfig(selectedEndpoint, authToken, {
      types: exportTypes.trim() || undefined,
      tags: exportTags.trim() || undefined,
      include_inactive: exportInactive || undefined
    })
    if (data) {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `mcp-config-${new Date().toISOString().slice(0, 10)}.json`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Configuration exported')
    }
    setExporting(false)
  }

  const handleImport = async () => {
    if (!importFile) return
    setImporting(true)
    setImportResult(null)
    try {
      const text = await importFile.text()
      const data = JSON.parse(text) as Record<string, unknown>
      const result = await importMCPConfig(
        selectedEndpoint,
        data,
        { conflict_strategy: conflictStrategy, dry_run: dryRun },
        authToken
      )
      if (result) {
        setImportResult(result)
        if (!dryRun) {
          toast.success('Configuration imported')
        }
      }
    } catch {
      toast.error('Invalid JSON file')
    }
    setImporting(false)
  }

  return (
    <div className="space-y-6">
      {/* Health Status */}
      <div className="rounded-lg border border-border p-4">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-medium">Gateway Health</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchHealth}
            disabled={healthLoading}
          >
            Refresh
          </Button>
        </div>
        {healthLoading ? (
          <p className="text-muted-foreground text-sm">Checking&hellip;</p>
        ) : health ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span
                className={`inline-block h-2 w-2 rounded-full ${
                  health.status === 'healthy'
                    ? 'bg-green-500'
                    : 'bg-destructive'
                }`}
              />
              <span className="text-sm">{health.status}</span>
              {health.version && (
                <span className="text-muted-foreground text-xs">
                  v{health.version}
                </span>
              )}
            </div>
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">Gateway unreachable.</p>
        )}
      </div>

      {/* Tags overview */}
      {tags.length > 0 && (
        <div className="rounded-lg border border-border p-4">
          <h3 className="mb-3 text-sm font-medium">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span
                key={tag.name}
                className="rounded bg-muted px-2 py-1 text-xs"
              >
                {tag.name}{' '}
                <span className="text-muted-foreground">
                  ({tag.stats.total})
                </span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Export */}
      <div className="rounded-lg border border-border p-4">
        <h3 className="mb-3 text-sm font-medium">Export Configuration</h3>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label
                htmlFor="export-types"
                className="mb-1 block text-xs font-medium"
              >
                Types (comma-separated)
              </label>
              <input
                id="export-types"
                type="text"
                value={exportTypes}
                onChange={(e) => setExportTypes(e.target.value)}
                placeholder="tools, resources, prompts"
                className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
              />
            </div>
            <div>
              <label
                htmlFor="export-tags"
                className="mb-1 block text-xs font-medium"
              >
                Tags (comma-separated)
              </label>
              <input
                id="export-tags"
                type="text"
                value={exportTags}
                onChange={(e) => setExportTags(e.target.value)}
                placeholder="production, staging"
                className="placeholder:text-muted-foreground focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-xs">
            <input
              type="checkbox"
              checked={exportInactive}
              onChange={(e) => setExportInactive(e.target.checked)}
              className="rounded border-border"
            />
            Include inactive entities
          </label>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
            disabled={exporting}
          >
            {exporting ? 'Exporting\u2026' : 'Export'}
          </Button>
        </div>
      </div>

      {/* Import */}
      {canConfigWrite && (
        <div className="rounded-lg border border-border p-4">
          <h3 className="mb-3 text-sm font-medium">Import Configuration</h3>
          <div className="space-y-3">
            <div>
              <label
                htmlFor="import-file"
                className="mb-1 block text-xs font-medium"
              >
                Configuration file (JSON)
              </label>
              <input
                id="import-file"
                type="file"
                accept=".json,application/json"
                onChange={(e) => setImportFile(e.target.files?.[0] ?? null)}
                className="text-muted-foreground w-full text-sm"
              />
            </div>
            <div>
              <label
                htmlFor="conflict-strategy"
                className="mb-1 block text-xs font-medium"
              >
                Conflict strategy
              </label>
              <select
                id="conflict-strategy"
                value={conflictStrategy}
                onChange={(e) => setConflictStrategy(e.target.value)}
                className="focus:ring-ring w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
              >
                <option value="update">Update (merge changes)</option>
                <option value="skip">Skip (keep existing)</option>
                <option value="rename">Rename (create copy)</option>
                <option value="fail">Fail (abort on conflict)</option>
              </select>
            </div>
            <label className="flex items-center gap-2 text-xs">
              <input
                type="checkbox"
                checked={dryRun}
                onChange={(e) => setDryRun(e.target.checked)}
                className="rounded border-border"
              />
              Dry run (preview changes without applying)
            </label>
            <Button
              variant="outline"
              size="sm"
              onClick={handleImport}
              disabled={importing || !importFile}
            >
              {importing ? 'Importing\u2026' : dryRun ? 'Preview' : 'Import'}
            </Button>
            {importResult && (
              <div className="rounded bg-muted p-3">
                <p className="mb-1 text-xs font-medium">
                  {dryRun ? 'Preview' : 'Import'} result: {importResult.status}
                </p>
                <pre className="max-h-32 overflow-auto text-xs">
                  {JSON.stringify(importResult.summary, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
