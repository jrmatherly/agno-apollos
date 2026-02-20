'use client'

import { useEffect } from 'react'
import { useMsal } from '@azure/msal-react'
import { InteractionStatus } from '@azure/msal-browser'
import { useAuth } from '@/auth'
import { isMsalConfigured } from '@/auth/msalConfig'

/**
 * Protects the chat UI when MSAL is configured.
 * Redirects unauthenticated users to Microsoft login once MSAL is ready.
 * No-op when MSAL is not configured (local dev without Entra ID).
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, login } = useAuth()
  const { inProgress } = useMsal()

  // Only call login() when MSAL has finished initializing (inProgress === None).
  // Calling it during 'startup' or 'handleRedirect' throws uninitialized_public_client_application.
  useEffect(() => {
    if (
      isMsalConfigured &&
      !isAuthenticated &&
      inProgress === InteractionStatus.None
    ) {
      login()
    }
  }, [isAuthenticated, inProgress]) // eslint-disable-line react-hooks/exhaustive-deps

  if (isMsalConfigured && !isAuthenticated) {
    return (
      <div className="flex h-screen items-center justify-center bg-background/80">
        <p className="text-muted-foreground text-sm">Redirecting to sign in…</p>
      </div>
    )
  }

  return <>{children}</>
}
