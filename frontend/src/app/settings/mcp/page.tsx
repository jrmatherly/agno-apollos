'use client'

import { useMemo } from 'react'
import Link from 'next/link'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useHasAnyScope } from '@/auth/useHasScope'
import { ServersTab } from './components/ServersTab'
import { ToolsTab } from './components/ToolsTab'
import { VirtualServersTab } from './components/VirtualServersTab'
import { ResourcesTab } from './components/ResourcesTab'
import { PromptsTab } from './components/PromptsTab'
import { ConfigTab } from './components/ConfigTab'

interface TabDef {
  value: string
  label: string
  scopes: string[]
  component: React.ComponentType
}

const ALL_TABS: TabDef[] = [
  {
    value: 'servers',
    label: 'Servers',
    scopes: ['mcp:servers:read'],
    component: ServersTab
  },
  {
    value: 'tools',
    label: 'Tools',
    scopes: ['mcp:tools:read'],
    component: ToolsTab
  },
  {
    value: 'virtual-servers',
    label: 'Virtual Servers',
    scopes: ['mcp:virtual-servers:read'],
    component: VirtualServersTab
  },
  {
    value: 'resources',
    label: 'Resources',
    scopes: ['mcp:resources:read'],
    component: ResourcesTab
  },
  {
    value: 'prompts',
    label: 'Prompts',
    scopes: ['mcp:prompts:read'],
    component: PromptsTab
  },
  {
    value: 'config',
    label: 'Config',
    scopes: ['mcp:config:read'],
    component: ConfigTab
  }
]

function FilteredTabs() {
  const canServers = useHasAnyScope('mcp:servers:read')
  const canTools = useHasAnyScope('mcp:tools:read')
  const canVS = useHasAnyScope('mcp:virtual-servers:read')
  const canResources = useHasAnyScope('mcp:resources:read')
  const canPrompts = useHasAnyScope('mcp:prompts:read')
  const canConfig = useHasAnyScope('mcp:config:read')

  const scopeMap: Record<string, boolean> = useMemo(
    () => ({
      servers: canServers,
      tools: canTools,
      'virtual-servers': canVS,
      resources: canResources,
      prompts: canPrompts,
      config: canConfig
    }),
    [canServers, canTools, canVS, canResources, canPrompts, canConfig]
  )

  const visibleTabs = useMemo(
    () => ALL_TABS.filter((t) => scopeMap[t.value]),
    [scopeMap]
  )

  if (visibleTabs.length === 0) {
    return (
      <div className="rounded-lg border border-border p-6">
        <p className="text-muted-foreground text-sm">
          You do not have permissions to view any MCP settings. Contact your
          administrator for access.
        </p>
      </div>
    )
  }

  return (
    <Tabs defaultValue={visibleTabs[0].value} className="w-full">
      <TabsList className="mb-4 flex w-full flex-wrap">
        {visibleTabs.map((tab) => (
          <TabsTrigger key={tab.value} value={tab.value}>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {visibleTabs.map((tab) => (
        <TabsContent key={tab.value} value={tab.value}>
          <tab.component />
        </TabsContent>
      ))}
    </Tabs>
  )
}

export default function MCPSettingsPage() {
  return (
    <AuthGuard>
      <div className="mx-auto max-w-4xl px-6 py-12">
        <Link
          href="/settings"
          className="text-muted-foreground hover:text-foreground mb-6 inline-block text-sm"
        >
          &larr; Settings
        </Link>
        <h1 className="mb-2 text-2xl font-semibold">MCP Gateway</h1>
        <p className="text-muted-foreground mb-8 text-sm">
          Manage MCP servers, tools, virtual servers, resources, and prompts
          through the ContextForge gateway.
        </p>
        <FilteredTabs />
      </div>
    </AuthGuard>
  )
}
