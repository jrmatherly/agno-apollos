export const APIRoutes = {
  GetAgents: (agentOSUrl: string) => `${agentOSUrl}/agents`,
  AgentRun: (agentOSUrl: string) => `${agentOSUrl}/agents/{agent_id}/runs`,
  Status: (agentOSUrl: string) => `${agentOSUrl}/health`,
  GetSessions: (agentOSUrl: string) => `${agentOSUrl}/sessions`,
  GetSession: (agentOSUrl: string, sessionId: string) =>
    `${agentOSUrl}/sessions/${sessionId}/runs`,

  DeleteSession: (agentOSUrl: string, sessionId: string) =>
    `${agentOSUrl}/sessions/${sessionId}`,

  GetTeams: (agentOSUrl: string) => `${agentOSUrl}/teams`,
  TeamRun: (agentOSUrl: string, teamId: string) =>
    `${agentOSUrl}/teams/${teamId}/runs`,
  DeleteTeamSession: (agentOSUrl: string, teamId: string, sessionId: string) =>
    `${agentOSUrl}/teams/${teamId}/sessions/${sessionId}`,

  M365Status: (agentOSUrl: string) => `${agentOSUrl}/m365/status`,
  M365Connect: (agentOSUrl: string) => `${agentOSUrl}/m365/connect`,
  M365Disconnect: (agentOSUrl: string) => `${agentOSUrl}/m365/disconnect`,

  // Auth
  AuthMe: (agentOSUrl: string) => `${agentOSUrl}/auth/me`,

  // MCP Gateways (registered upstream MCP servers)
  MCPServers: (agentOSUrl: string) => `${agentOSUrl}/mcp/servers`,
  MCPServer: (agentOSUrl: string, serverId: string) =>
    `${agentOSUrl}/mcp/servers/${serverId}`,
  MCPServerState: (agentOSUrl: string, serverId: string) =>
    `${agentOSUrl}/mcp/servers/${serverId}/state`,
  MCPServerRefresh: (agentOSUrl: string, serverId: string) =>
    `${agentOSUrl}/mcp/servers/${serverId}/refresh`,

  // MCP Tools
  MCPTools: (agentOSUrl: string) => `${agentOSUrl}/mcp/tools`,
  MCPTool: (agentOSUrl: string, toolId: string) =>
    `${agentOSUrl}/mcp/tools/${toolId}`,
  MCPToolState: (agentOSUrl: string, toolId: string) =>
    `${agentOSUrl}/mcp/tools/${toolId}/state`,

  // MCP Virtual Servers
  MCPVirtualServers: (agentOSUrl: string) =>
    `${agentOSUrl}/mcp/virtual-servers`,
  MCPVirtualServer: (agentOSUrl: string, vsId: string) =>
    `${agentOSUrl}/mcp/virtual-servers/${vsId}`,
  MCPVirtualServerState: (agentOSUrl: string, vsId: string) =>
    `${agentOSUrl}/mcp/virtual-servers/${vsId}/state`,
  MCPVirtualServerTools: (agentOSUrl: string, vsId: string) =>
    `${agentOSUrl}/mcp/virtual-servers/${vsId}/tools`,
  MCPVirtualServerResources: (agentOSUrl: string, vsId: string) =>
    `${agentOSUrl}/mcp/virtual-servers/${vsId}/resources`,
  MCPVirtualServerPrompts: (agentOSUrl: string, vsId: string) =>
    `${agentOSUrl}/mcp/virtual-servers/${vsId}/prompts`,

  // MCP Resources
  MCPResources: (agentOSUrl: string) => `${agentOSUrl}/mcp/resources`,
  MCPResource: (agentOSUrl: string, resourceId: string) =>
    `${agentOSUrl}/mcp/resources/${resourceId}`,
  MCPResourceInfo: (agentOSUrl: string, resourceId: string) =>
    `${agentOSUrl}/mcp/resources/${resourceId}/info`,
  MCPResourceState: (agentOSUrl: string, resourceId: string) =>
    `${agentOSUrl}/mcp/resources/${resourceId}/state`,
  MCPResourceTemplates: (agentOSUrl: string) =>
    `${agentOSUrl}/mcp/resources/templates`,

  // MCP Prompts
  MCPPrompts: (agentOSUrl: string) => `${agentOSUrl}/mcp/prompts`,
  MCPPrompt: (agentOSUrl: string, promptId: string) =>
    `${agentOSUrl}/mcp/prompts/${promptId}`,
  MCPPromptState: (agentOSUrl: string, promptId: string) =>
    `${agentOSUrl}/mcp/prompts/${promptId}/state`,

  // MCP Tags
  MCPTags: (agentOSUrl: string) => `${agentOSUrl}/mcp/tags`,
  MCPTagEntities: (agentOSUrl: string, tagName: string) =>
    `${agentOSUrl}/mcp/tags/${tagName}`,

  // MCP Import/Export
  MCPExport: (agentOSUrl: string) => `${agentOSUrl}/mcp/export`,
  MCPImport: (agentOSUrl: string) => `${agentOSUrl}/mcp/import`,
  MCPImportStatus: (agentOSUrl: string, importId: string) =>
    `${agentOSUrl}/mcp/import/status/${importId}`,

  // MCP Health
  MCPHealth: (agentOSUrl: string) => `${agentOSUrl}/mcp/health`,

  // MCP Preferences
  MCPPreferences: (agentOSUrl: string) => `${agentOSUrl}/mcp/preferences`
}
