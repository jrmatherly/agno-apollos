'use client'

import { useEffect } from 'react'
import { useStore } from '@/store'
import { APIRoutes } from '@/api/routes'
import { useAuth } from './useAuth'
import { isMsalConfigured } from './msalConfig'

const REFRESH_INTERVAL_MS = 5 * 60 * 1000 // 5 minutes — well within Entra's 1-hour token lifetime

/**
 * Syncs the current MSAL access token into Zustand's authToken.
 * - On mount: immediately acquires and stores the token
 * - Every 5 minutes: refreshes silently (MSAL handles the actual OAuth refresh)
 * - On logout: clears the token
 * - After token sync: fetches user scopes from /auth/me
 *
 * No-op when isMsalConfigured is false — safe to call regardless.
 */
export function useTokenSync() {
  const { isAuthenticated, getAccessToken } = useAuth()
  const { selectedEndpoint, setAuthToken, setUserScopes } = useStore()

  useEffect(() => {
    if (!isMsalConfigured) return

    const sync = async () => {
      if (isAuthenticated) {
        const token = await getAccessToken()
        setAuthToken(token ?? '')

        // Fetch user scopes after token acquisition
        if (token) {
          try {
            const resp = await fetch(APIRoutes.AuthMe(selectedEndpoint), {
              headers: { Authorization: `Bearer ${token}` }
            })
            if (resp.ok) {
              const data = await resp.json()
              setUserScopes((data as { scopes?: string[] }).scopes ?? [])
            }
          } catch {
            // Scope fetch is best-effort — don't block auth flow
          }
        }
      } else {
        setAuthToken('')
        setUserScopes([])
      }
    }

    sync()
    const interval = setInterval(sync, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]) // Intentionally omitting stable refs
}
