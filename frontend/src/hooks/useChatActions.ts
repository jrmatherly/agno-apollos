import { useCallback } from 'react'
import { toast } from 'sonner'

import { useStore } from '../store'

import { type ChatMessage } from '@/types/os'
import { getAgentsAPI, getStatusAPI, getTeamsAPI } from '@/api/os'
import { APIRoutes } from '@/api/routes'
import { constructEndpointUrl } from '@/lib/constructEndpointUrl'
import { useQueryState } from 'nuqs'

const useChatActions = () => {
  const { chatInputRef } = useStore()
  const selectedEndpoint = useStore((state) => state.selectedEndpoint)
  const authToken = useStore((state) => state.authToken)
  const [, setSessionId] = useQueryState('session')
  const setMessages = useStore((state) => state.setMessages)
  const setIsEndpointActive = useStore((state) => state.setIsEndpointActive)
  const setIsEndpointLoading = useStore((state) => state.setIsEndpointLoading)
  const setTeams = useStore((state) => state.setTeams)
  const setSelectedModel = useStore((state) => state.setSelectedModel)
  const setMode = useStore((state) => state.setMode)
  const [, setAgentId] = useQueryState('agent')
  const [, setTeamId] = useQueryState('team')
  const [, setDbId] = useQueryState('db_id')

  const getStatus = useCallback(async () => {
    try {
      const status = await getStatusAPI(selectedEndpoint, authToken)
      return status
    } catch {
      return 503
    }
  }, [selectedEndpoint, authToken])

  const getAgents = useCallback(async () => {
    try {
      const agents = await getAgentsAPI(selectedEndpoint, authToken)
      return agents
    } catch {
      toast.error('Error fetching agents')
      return []
    }
  }, [selectedEndpoint, authToken])

  const getTeams = useCallback(async () => {
    try {
      const teams = await getTeamsAPI(selectedEndpoint, authToken)
      return teams
    } catch {
      toast.error('Error fetching teams')
      return []
    }
  }, [selectedEndpoint, authToken])

  const clearChat = useCallback(() => {
    setMessages([])
    setSessionId(null)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const focusChatInput = useCallback(() => {
    setTimeout(() => {
      requestAnimationFrame(() => chatInputRef?.current?.focus())
    }, 0)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const addMessage = useCallback(
    (message: ChatMessage) => {
      setMessages((prevMessages) => [...prevMessages, message])
    },
    [setMessages]
  )

  const initialize = useCallback(async () => {
    setIsEndpointLoading(true)
    try {
      const status = await getStatus()
      if (status === 200) {
        setIsEndpointActive(true)
        // Fetch teams for session listing (coordinator team manages sessions)
        const teams = await getTeams()
        setTeams(teams)

        // Clear any stale agent query param from bookmarked URLs
        setAgentId(null)

        // Set coordinator team as the active team for session management
        const coordinator = teams.find((t) => t.id === 'apollos-coordinator')
        if (coordinator) {
          setTeamId(coordinator.id)
          setMode('team')
          setSelectedModel(coordinator.model?.provider || '')
          setDbId(coordinator.db_id || '')
        }

        // Check M365 connection status for toggle gating
        try {
          const m365Res = await fetch(
            APIRoutes.M365Status(constructEndpointUrl(selectedEndpoint)),
            {
              headers: authToken ? { Authorization: `Bearer ${authToken}` } : {}
            }
          )
          if (m365Res.ok) {
            const m365Data = await m365Res.json()
            useStore.getState().setM365Connected(m365Data.connected === true)
          }
        } catch {
          // M365 not available or not enabled — leave as disconnected
        }
      } else {
        setIsEndpointActive(false)
        setSelectedModel('')
        setAgentId(null)
        setTeamId(null)
      }
    } catch (error) {
      console.error('Error initializing:', error)
      setIsEndpointActive(false)
      setSelectedModel('')
      setAgentId(null)
      setTeamId(null)
      setTeams([])
    } finally {
      setIsEndpointLoading(false)
    }
  }, [
    getStatus,
    getTeams,
    setIsEndpointActive,
    setIsEndpointLoading,
    setTeams,
    setAgentId,
    setTeamId,
    setSelectedModel,
    setMode,
    setDbId,
    selectedEndpoint,
    authToken
  ])

  return {
    clearChat,
    addMessage,
    getAgents,
    focusChatInput,
    getTeams,
    initialize
  }
}

export default useChatActions
