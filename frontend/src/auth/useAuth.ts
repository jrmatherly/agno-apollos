'use client'

import { InteractionRequiredAuthError } from '@azure/msal-browser'
import { useIsAuthenticated, useMsal } from '@azure/msal-react'
import { apiScopes } from './msalConfig'

/**
 * Project-specific auth hook. Wraps useMsal() with our API scopes.
 * Only call from components inside <AuthProvider>.
 */
export function useAuth() {
  const { instance, accounts } = useMsal()
  const isAuthenticated = useIsAuthenticated()
  const account = accounts[0] ?? null

  /**
   * Silently acquires an access token for the backend API scope.
   * Falls back to redirect if interaction is required (expired refresh token, MFA).
   * Returns null if not authenticated.
   */
  const getAccessToken = async (): Promise<string | null> => {
    if (!account) return null

    try {
      const result = await instance.acquireTokenSilent({
        scopes: apiScopes,
        account
      })
      return result.accessToken
    } catch (err) {
      if (err instanceof InteractionRequiredAuthError) {
        // Triggers a page redirect to Microsoft login — user will return authenticated
        await instance.acquireTokenRedirect({ scopes: apiScopes })
      } else {
        console.error('[MSAL] acquireTokenSilent failed (non-interactive error):', err)
      }
      return null
    }
  }

  const login = () =>
    instance.loginRedirect({
      scopes: apiScopes,
      prompt: 'select_account' // Force account picker on multi-account browsers
    })

  const logout = () => instance.logoutRedirect()

  return { isAuthenticated, account, getAccessToken, login, logout }
}
