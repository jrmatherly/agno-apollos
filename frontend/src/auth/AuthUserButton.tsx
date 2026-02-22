'use client'

import { Button } from '@/components/ui/button'
import Icon from '@/components/ui/icon'
import { useAuth } from './useAuth'
import { useTokenSync } from './useTokenSync'

/**
 * Sidebar auth control for MSAL-configured deployments.
 * Syncs the MSAL token to store on mount and every 5 minutes.
 */
export function AuthUserButton() {
  // Keep Zustand authToken in sync with MSAL
  useTokenSync()

  const { isAuthenticated, account, login, logout } = useAuth()

  if (!isAuthenticated) {
    return (
      <div className="flex flex-col items-start gap-2">
        <div className="text-xs font-medium text-primary">Auth</div>
        <Button
          variant="ghost"
          onClick={login}
          className="h-9 w-full rounded-xl border border-primary/15 bg-accent text-xs font-medium text-muted hover:bg-accent/80"
        >
          <Icon type="user" size="xs" />
          Sign In
        </Button>
      </div>
    )
  }

  const displayName =
    account?.name || account?.username || account?.localAccountId || 'Signed In'

  return (
    <div className="flex flex-col items-start gap-2">
      <div className="text-xs font-medium text-primary">Signed In</div>
      <div className="flex w-full items-center gap-1">
        <div className="flex h-9 flex-1 items-center truncate rounded-xl border border-primary/15 bg-accent px-3 text-xs font-medium text-muted">
          {displayName}
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={logout}
          className="shrink-0 hover:cursor-pointer hover:bg-transparent"
          title="Sign out"
        >
          <Icon type="x" size="xs" />
        </Button>
      </div>
    </div>
  )
}
