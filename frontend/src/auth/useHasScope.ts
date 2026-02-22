import { useStore } from '@/store'

export function useHasScope(scope: string): boolean {
  const { userScopes } = useStore()
  return userScopes.includes(scope) || userScopes.includes('agent_os:admin')
}

export function useHasAnyScope(...scopes: string[]): boolean {
  const { userScopes } = useStore()
  if (userScopes.includes('agent_os:admin')) return true
  return scopes.some((s) => userScopes.includes(s))
}
