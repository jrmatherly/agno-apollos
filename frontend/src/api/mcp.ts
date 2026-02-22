import { toast } from 'sonner'

import { APIRoutes } from './routes'

const createHeaders = (authToken?: string): HeadersInit => {
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`
  }
  return headers
}

// ── Constrained Types ───────────────────────────────────────────────────

export type MCPVisibility = 'public' | 'private' | 'team'
export type MCPTab =
  | 'servers'
  | 'tools'
  | 'virtual-servers'
  | 'resources'
  | 'prompts'
  | 'config'

// ── Interfaces ──────────────────────────────────────────────────────────

export interface MCPServerInfo {
  id: string
  name: string
  url: string
  status?: string | null
}

export interface MCPToolInfo {
  id: string
  name: string
  description?: string | null
  gateway_id?: string | null
  tags: string[]
  is_active: boolean
  input_schema?: Record<string, unknown> | null
  annotations?: Record<string, unknown> | null
  visibility?: MCPVisibility | null
  team_id?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface MCPVirtualServerInfo {
  id: string
  name: string
  description?: string | null
  is_active: boolean
  tags: string[]
  visibility?: MCPVisibility | null
  team_id?: string | null
}

export interface MCPResourceInfo {
  id: string
  name: string
  uri?: string | null
  description?: string | null
  mime_type?: string | null
  is_active: boolean
  annotations?: Record<string, unknown> | null
  visibility?: MCPVisibility | null
  team_id?: string | null
}

export interface MCPPromptArgument {
  name: string
  description?: string | null
  required: boolean
}

export interface MCPPromptInfo {
  id: string
  name: string
  description?: string | null
  is_active: boolean
  arguments: MCPPromptArgument[]
  visibility?: MCPVisibility | null
  team_id?: string | null
}

export interface MCPTagStats {
  tools: number
  resources: number
  prompts: number
  servers: number
  gateways: number
  total: number
}

export interface MCPTagInfo {
  name: string
  stats: MCPTagStats
  entities: Record<string, unknown>[]
}

export interface MCPHealthInfo {
  status: string
  version?: string | null
}

export interface MCPUserPreferences {
  hidden_tools: string[]
  hidden_servers: string[]
  default_tab: MCPTab
  compact_view: boolean
}

export interface MCPImportResult {
  import_id?: string | null
  status: string
  summary: Record<string, unknown>
}

// ── Helpers ─────────────────────────────────────────────────────────────

const extractError = async (
  resp: Response,
  fallback: string
): Promise<string> => {
  const data = await resp.json().catch(() => ({}))
  return (data as { detail?: string }).detail || fallback
}

// ── Gateways (registered upstream MCP servers) ──────────────────────────

export const listMCPServers = async (
  endpoint: string,
  authToken?: string
): Promise<MCPServerInfo[]> => {
  try {
    const resp = await fetch(APIRoutes.MCPServers(endpoint), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      if (resp.status === 503) return []
      toast.error(`Failed to fetch MCP servers: ${resp.statusText}`)
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

export const registerMCPServer = async (
  endpoint: string,
  name: string,
  url: string,
  authToken?: string
): Promise<MCPServerInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPServers(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify({ name, url })
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to register server'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to register server')
    return null
  }
}

export const updateMCPServer = async (
  endpoint: string,
  serverId: string,
  data: { name?: string; description?: string },
  authToken?: string
): Promise<MCPServerInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPServer(endpoint, serverId), {
      method: 'PUT',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to update server'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to update server')
    return null
  }
}

export const deleteMCPServer = async (
  endpoint: string,
  serverId: string,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPServer(endpoint, serverId), {
      method: 'DELETE',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to remove server'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to remove server')
    return false
  }
}

export const toggleMCPServer = async (
  endpoint: string,
  serverId: string,
  activate: boolean,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPServerState(endpoint, serverId), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify({ activate })
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to toggle server'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to toggle server')
    return false
  }
}

export const refreshMCPServer = async (
  endpoint: string,
  serverId: string,
  authToken?: string
): Promise<Record<string, unknown> | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPServerRefresh(endpoint, serverId), {
      method: 'POST',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to refresh server'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to refresh server')
    return null
  }
}

// ── Tools ───────────────────────────────────────────────────────────────

export const listMCPTools = async (
  endpoint: string,
  authToken?: string,
  params?: { gateway_id?: string; include_inactive?: boolean }
): Promise<MCPToolInfo[]> => {
  try {
    const url = new URL(APIRoutes.MCPTools(endpoint))
    if (params?.gateway_id)
      url.searchParams.set('gateway_id', params.gateway_id)
    if (params?.include_inactive)
      url.searchParams.set('include_inactive', 'true')
    const resp = await fetch(url.toString(), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      if (resp.status === 503) return []
      toast.error(`Failed to fetch tools: ${resp.statusText}`)
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

export const createMCPTool = async (
  endpoint: string,
  data: {
    name: string
    description?: string
    tags?: string[]
    team_id?: string
    visibility?: string
  },
  authToken?: string
): Promise<MCPToolInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPTools(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to create tool'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to create tool')
    return null
  }
}

export const updateMCPTool = async (
  endpoint: string,
  toolId: string,
  data: { name?: string; description?: string; tags?: string[] },
  authToken?: string
): Promise<MCPToolInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPTool(endpoint, toolId), {
      method: 'PUT',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to update tool'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to update tool')
    return null
  }
}

export const toggleMCPTool = async (
  endpoint: string,
  toolId: string,
  activate: boolean,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPToolState(endpoint, toolId), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify({ activate })
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to toggle tool'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to toggle tool')
    return false
  }
}

export const deleteMCPTool = async (
  endpoint: string,
  toolId: string,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPTool(endpoint, toolId), {
      method: 'DELETE',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to delete tool'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to delete tool')
    return false
  }
}

// ── Virtual Servers ─────────────────────────────────────────────────────

export const listMCPVirtualServers = async (
  endpoint: string,
  authToken?: string,
  params?: { include_inactive?: boolean }
): Promise<MCPVirtualServerInfo[]> => {
  try {
    const url = new URL(APIRoutes.MCPVirtualServers(endpoint))
    if (params?.include_inactive)
      url.searchParams.set('include_inactive', 'true')
    const resp = await fetch(url.toString(), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      if (resp.status === 503) return []
      toast.error(`Failed to fetch virtual servers: ${resp.statusText}`)
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

export const createMCPVirtualServer = async (
  endpoint: string,
  data: {
    name: string
    description?: string
    team_id?: string
    visibility?: string
  },
  authToken?: string
): Promise<MCPVirtualServerInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPVirtualServers(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to create virtual server'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to create virtual server')
    return null
  }
}

export const updateMCPVirtualServer = async (
  endpoint: string,
  vsId: string,
  data: { name?: string; description?: string },
  authToken?: string
): Promise<MCPVirtualServerInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPVirtualServer(endpoint, vsId), {
      method: 'PUT',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to update virtual server'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to update virtual server')
    return null
  }
}

export const toggleMCPVirtualServer = async (
  endpoint: string,
  vsId: string,
  activate: boolean,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPVirtualServerState(endpoint, vsId), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify({ activate })
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to toggle virtual server'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to toggle virtual server')
    return false
  }
}

export const deleteMCPVirtualServer = async (
  endpoint: string,
  vsId: string,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPVirtualServer(endpoint, vsId), {
      method: 'DELETE',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to delete virtual server'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to delete virtual server')
    return false
  }
}

export const listMCPVirtualServerTools = async (
  endpoint: string,
  vsId: string,
  authToken?: string
): Promise<MCPToolInfo[]> => {
  try {
    const resp = await fetch(APIRoutes.MCPVirtualServerTools(endpoint, vsId), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      if (resp.status !== 503)
        toast.error(`Failed to fetch virtual server tools: ${resp.statusText}`)
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

export const listMCPVirtualServerResources = async (
  endpoint: string,
  vsId: string,
  authToken?: string
): Promise<MCPResourceInfo[]> => {
  try {
    const resp = await fetch(
      APIRoutes.MCPVirtualServerResources(endpoint, vsId),
      {
        method: 'GET',
        headers: createHeaders(authToken)
      }
    )
    if (!resp.ok) {
      if (resp.status !== 503)
        toast.error(
          `Failed to fetch virtual server resources: ${resp.statusText}`
        )
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

export const listMCPVirtualServerPrompts = async (
  endpoint: string,
  vsId: string,
  authToken?: string
): Promise<MCPPromptInfo[]> => {
  try {
    const resp = await fetch(
      APIRoutes.MCPVirtualServerPrompts(endpoint, vsId),
      {
        method: 'GET',
        headers: createHeaders(authToken)
      }
    )
    if (!resp.ok) {
      if (resp.status !== 503)
        toast.error(
          `Failed to fetch virtual server prompts: ${resp.statusText}`
        )
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

// ── Resources ───────────────────────────────────────────────────────────

export const listMCPResources = async (
  endpoint: string,
  authToken?: string,
  params?: { include_inactive?: boolean }
): Promise<MCPResourceInfo[]> => {
  try {
    const url = new URL(APIRoutes.MCPResources(endpoint))
    if (params?.include_inactive)
      url.searchParams.set('include_inactive', 'true')
    const resp = await fetch(url.toString(), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      if (resp.status === 503) return []
      toast.error(`Failed to fetch resources: ${resp.statusText}`)
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

export const createMCPResource = async (
  endpoint: string,
  data: {
    name: string
    uri?: string
    description?: string
    mime_type?: string
    team_id?: string
    visibility?: string
  },
  authToken?: string
): Promise<MCPResourceInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPResources(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to create resource'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to create resource')
    return null
  }
}

export const updateMCPResource = async (
  endpoint: string,
  resourceId: string,
  data: { name?: string; description?: string },
  authToken?: string
): Promise<MCPResourceInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPResource(endpoint, resourceId), {
      method: 'PUT',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to update resource'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to update resource')
    return null
  }
}

export const toggleMCPResource = async (
  endpoint: string,
  resourceId: string,
  activate: boolean,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPResourceState(endpoint, resourceId), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify({ activate })
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to toggle resource'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to toggle resource')
    return false
  }
}

export const deleteMCPResource = async (
  endpoint: string,
  resourceId: string,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPResource(endpoint, resourceId), {
      method: 'DELETE',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to delete resource'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to delete resource')
    return false
  }
}

// ── Prompts ─────────────────────────────────────────────────────────────

export const listMCPPrompts = async (
  endpoint: string,
  authToken?: string,
  params?: { include_inactive?: boolean }
): Promise<MCPPromptInfo[]> => {
  try {
    const url = new URL(APIRoutes.MCPPrompts(endpoint))
    if (params?.include_inactive)
      url.searchParams.set('include_inactive', 'true')
    const resp = await fetch(url.toString(), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      if (resp.status === 503) return []
      toast.error(`Failed to fetch prompts: ${resp.statusText}`)
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

export const createMCPPrompt = async (
  endpoint: string,
  data: {
    name: string
    description?: string
    team_id?: string
    visibility?: string
  },
  authToken?: string
): Promise<MCPPromptInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPPrompts(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to create prompt'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to create prompt')
    return null
  }
}

export const updateMCPPrompt = async (
  endpoint: string,
  promptId: string,
  data: { name?: string; description?: string },
  authToken?: string
): Promise<MCPPromptInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPPrompt(endpoint, promptId), {
      method: 'PUT',
      headers: createHeaders(authToken),
      body: JSON.stringify(data)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to update prompt'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to update prompt')
    return null
  }
}

export const toggleMCPPrompt = async (
  endpoint: string,
  promptId: string,
  activate: boolean,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPPromptState(endpoint, promptId), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify({ activate })
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to toggle prompt'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to toggle prompt')
    return false
  }
}

export const deleteMCPPrompt = async (
  endpoint: string,
  promptId: string,
  authToken?: string
): Promise<boolean> => {
  try {
    const resp = await fetch(APIRoutes.MCPPrompt(endpoint, promptId), {
      method: 'DELETE',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to delete prompt'))
      return false
    }
    return true
  } catch {
    toast.error('Failed to delete prompt')
    return false
  }
}

// ── Tags ────────────────────────────────────────────────────────────────

export const listMCPTags = async (
  endpoint: string,
  authToken?: string
): Promise<MCPTagInfo[]> => {
  try {
    const resp = await fetch(APIRoutes.MCPTags(endpoint), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      if (resp.status === 503) return []
      toast.error(`Failed to fetch tags: ${resp.statusText}`)
      return []
    }
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return []
  }
}

export const getMCPTagEntities = async (
  endpoint: string,
  tagName: string,
  authToken?: string
): Promise<Record<string, unknown> | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPTagEntities(endpoint, tagName), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) return null
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return null
  }
}

// ── Import/Export ────────────────────────────────────────────────────────

export const exportMCPConfig = async (
  endpoint: string,
  authToken?: string,
  params?: {
    types?: string
    tags?: string
    include_inactive?: boolean
  }
): Promise<Record<string, unknown> | null> => {
  try {
    const url = new URL(APIRoutes.MCPExport(endpoint))
    if (params?.types) url.searchParams.set('types', params.types)
    if (params?.tags) url.searchParams.set('tags', params.tags)
    if (params?.include_inactive)
      url.searchParams.set('include_inactive', 'true')
    const resp = await fetch(url.toString(), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to export config'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to export config')
    return null
  }
}

export const importMCPConfig = async (
  endpoint: string,
  data: Record<string, unknown>,
  options?: { conflict_strategy?: string; dry_run?: boolean },
  authToken?: string
): Promise<MCPImportResult | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPImport(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify({
        data,
        conflict_strategy: options?.conflict_strategy ?? 'update',
        dry_run: options?.dry_run ?? false
      })
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to import config'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to import config')
    return null
  }
}

export const getMCPImportStatus = async (
  endpoint: string,
  importId: string,
  authToken?: string
): Promise<Record<string, unknown> | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPImportStatus(endpoint, importId), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) return null
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return null
  }
}

// ── Health ───────────────────────────────────────────────────────────────

export const getMCPHealth = async (
  endpoint: string,
  authToken?: string
): Promise<MCPHealthInfo | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPHealth(endpoint), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) return null
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return null
  }
}

// ── Preferences ─────────────────────────────────────────────────────────

export const getMCPPreferences = async (
  endpoint: string,
  authToken?: string
): Promise<MCPUserPreferences | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPPreferences(endpoint), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) return null
    return await resp.json()
  } catch (err) {
    console.error('MCP API error:', err)
    return null
  }
}

export const updateMCPPreferences = async (
  endpoint: string,
  prefs: MCPUserPreferences,
  authToken?: string
): Promise<MCPUserPreferences | null> => {
  try {
    const resp = await fetch(APIRoutes.MCPPreferences(endpoint), {
      method: 'PUT',
      headers: createHeaders(authToken),
      body: JSON.stringify(prefs)
    })
    if (!resp.ok) {
      toast.error(await extractError(resp, 'Failed to update preferences'))
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to update preferences')
    return null
  }
}
