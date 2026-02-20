'use client'

import { useEffect } from 'react'
import { useStore } from '@/store'
import { useAuth } from './useAuth'
import { isMsalConfigured } from './msalConfig'

const REFRESH_INTERVAL_MS = 5 * 60 * 1000 // 5 minutes — well within Entra's 1-hour token lifetime

/**
 * Syncs the current MSAL access token into Zustand's authToken.
 * - On mount: immediately acquires and stores the token
 * - Every 5 minutes: refreshes silently (MSAL handles the actual OAuth refresh)
 * - On logout: clears the token
 *
 * No-op when isMsalConfigured is false — safe to call regardless.
 */
export function useTokenSync() {
  const { isAuthenticated, getAccessToken } = useAuth()
  const { setAuthToken } = useStore()

  useEffect(() => {
    if (!isMsalConfigured) return

    const sync = async () => {
      if (isAuthenticated) {
        const token = await getAccessToken()
        setAuthToken(token ?? '')
      } else {
        setAuthToken('')
      }
    }

    sync()
    const interval = setInterval(sync, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]) // Intentionally omitting getAccessToken/setAuthToken (stable refs)
}
