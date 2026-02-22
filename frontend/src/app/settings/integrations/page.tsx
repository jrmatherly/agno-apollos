'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function IntegrationsPage() {
  const router = useRouter()
  useEffect(() => {
    router.replace('/settings/mcp')
  }, [router])
  return null
}
