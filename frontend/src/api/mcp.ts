import { toast } from 'sonner'

import { APIRoutes } from './routes'

const createHeaders = (authToken?: string): HeadersInit => {
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`
  }
  return headers
}

export interface MCPServerInfo {
  id: string
  name: string
  url: string
  status?: string | null
}

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
  } catch {
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
      const data = await resp.json().catch(() => ({}))
      toast.error(
        (data as { detail?: string }).detail || 'Failed to register server'
      )
      return null
    }
    return await resp.json()
  } catch {
    toast.error('Failed to register server')
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
      const data = await resp.json().catch(() => ({}))
      toast.error(
        (data as { detail?: string }).detail || 'Failed to remove server'
      )
      return false
    }
    return true
  } catch {
    toast.error('Failed to remove server')
    return false
  }
}
