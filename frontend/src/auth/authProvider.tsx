'use client'

import { MsalProvider } from '@azure/msal-react'
import { isMsalConfigured, msalInstance } from './msalConfig'

interface AuthProviderProps {
  children: React.ReactNode
}

/**
 * Wraps the app with MsalProvider when Entra ID is configured.
 * Passes children through unchanged when NEXT_PUBLIC_AZURE_CLIENT_ID is empty.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  if (!isMsalConfigured || !msalInstance) {
    return <>{children}</>
  }
  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>
}
