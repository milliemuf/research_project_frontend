import { ref } from 'vue'
import { useBugsStore } from '@/stores/bugs'
import { useAgentsStore } from '@/stores/agents'
import { useConsensusStore } from '@/stores/consensus'

const socket = ref(null)
const connected = ref(false)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 5

export function useWebSocket() {
  function connect() {
    const envWs = import.meta.env.VITE_WS_URL
    const apiUrl = import.meta.env.VITE_API_URL
    let wsUrl
    if (envWs) {
      wsUrl = envWs
    } else if (apiUrl) {
      wsUrl = apiUrl.replace(/^http/, 'ws').replace(/\/$/, '') + '/ws/live'
    } else {
      wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/live`
    }

    try {
      socket.value = new WebSocket(wsUrl)

      socket.value.onopen = () => {
        console.log('WebSocket connected')
        connected.value = true
        reconnectAttempts.value = 0
      }

      socket.value.onmessage = (event) => {
        handleMessage(JSON.parse(event.data))
      }

      socket.value.onclose = () => {
        console.log('WebSocket disconnected')
        connected.value = false
        attemptReconnect()
      }

      socket.value.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      attemptReconnect()
    }
  }

  function disconnect() {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
  }

  function attemptReconnect() {
    if (reconnectAttempts.value < maxReconnectAttempts) {
      reconnectAttempts.value++
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 30000)
      console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttempts.value})`)
      setTimeout(connect, delay)
    }
  }

  function handleMessage(message) {
    const { event, data } = message
    const bugsStore = useBugsStore()
    const agentsStore = useAgentsStore()
    const consensusStore = useConsensusStore()

    switch (event) {
      case 'connected':
        console.log('Connected to live updates:', data.message)
        break

      case 'bug_detected':
        bugsStore.addBug(data)
        break

      case 'bug_updated':
        bugsStore.updateBug(data)
        break

      case 'consensus_started':
        consensusStore.startRound(data)
        break

      case 'consensus_update':
        if (data.phase) {
          consensusStore.updateRoundPhase(data.round_id, data.phase, data)
        }
        if (data.prepare_vote) {
          consensusStore.addPrepareVote(data.round_id, data.prepare_vote)
        }
        if (data.commit_vote) {
          consensusStore.addCommitVote(data.round_id, data.commit_vote)
        }
        break

      case 'consensus_completed':
        consensusStore.completeRound(data.round_id, data.success, data.reason)
        break

      case 'fix_applied':
        bugsStore.updateBug(data.bug)
        break

      case 'agent_status_change':
        agentsStore.updateAgentStatus(data.agent_id, data.status)
        break

      default:
        console.log('Unknown event:', event, data)
    }
  }

  function send(message) {
    if (socket.value && connected.value) {
      socket.value.send(JSON.stringify(message))
    }
  }

  function subscribe(channel) {
    send({ action: 'subscribe', channel })
  }

  return {
    socket,
    connected,
    connect,
    disconnect,
    send,
    subscribe
  }
}
