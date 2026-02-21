import { toast } from 'sonner'

import { APIRoutes } from './routes'

const createHeaders = (authToken?: string): HeadersInit => {
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`
  }
  return headers
}

export interface M365Status {
  connected: boolean
  scopes?: string[]
  account?: string
  needs_reconnect?: boolean
}

export const getM365Status = async (
  endpoint: string,
  authToken?: string
): Promise<M365Status> => {
  try {
    const resp = await fetch(APIRoutes.M365Status(endpoint), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!resp.ok) return { connected: false }
    return await resp.json()
  } catch {
    return { connected: false }
  }
}

export const connectM365 = async (
  endpoint: string,
  authToken?: string
): Promise<{ connected: boolean; error?: string }> => {
  try {
    const resp = await fetch(APIRoutes.M365Connect(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken)
    })
    const data = await resp.json()
    if (!resp.ok) {
      toast.error(data.detail || 'Failed to connect Microsoft 365')
      return { connected: false, error: data.detail }
    }
    return data
  } catch {
    toast.error('Connection failed')
    return { connected: false, error: 'Connection failed' }
  }
}

export const disconnectM365 = async (
  endpoint: string,
  authToken?: string
): Promise<void> => {
  try {
    await fetch(APIRoutes.M365Disconnect(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken)
    })
  } catch {
    toast.error('Failed to disconnect')
  }
}
