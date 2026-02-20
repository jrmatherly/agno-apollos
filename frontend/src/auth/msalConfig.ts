import {
  PublicClientApplication,
  type Configuration
} from '@azure/msal-browser'

const clientId = process.env.NEXT_PUBLIC_AZURE_CLIENT_ID ?? ''
const tenantId = process.env.NEXT_PUBLIC_AZURE_TENANT_ID ?? ''

/** True when all MSAL config env vars are set. Controls conditional rendering. */
export const isMsalConfigured = clientId.length > 0 && tenantId.length > 0

function createMsalInstance(): PublicClientApplication | null {
  if (!isMsalConfigured) return null
  // Guard: PublicClientApplication uses browser APIs (sessionStorage, window).
  // Do not create during SSR — typeof window check ensures browser-only init.
  if (typeof window === 'undefined') return null

  const config: Configuration = {
    auth: {
      clientId,
      authority: `https://login.microsoftonline.com/${tenantId}`,
      redirectUri:
        process.env.NEXT_PUBLIC_REDIRECT_URI ?? 'http://localhost:3000'
    },
    cache: {
      cacheLocation: 'sessionStorage' // Scoped to tab — more secure than localStorage
    }
  }
  return new PublicClientApplication(config)
}

/** The MSAL instance. Null when MSAL is not configured or during SSR. */
export const msalInstance = createMsalInstance()

/** Scopes requested when acquiring access tokens for the backend API. */
export const apiScopes = [`api://${clientId}/access_as_user`]
