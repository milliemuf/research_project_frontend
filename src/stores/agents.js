import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAgentsStore = defineStore('agents', () => {
  // State
  const agents = ref([])
  const consensusStatus = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const onlineAgents = computed(() =>
    agents.value.filter(a => a.status === 'online')
  )

  const analyzerAgents = computed(() =>
    agents.value.filter(a => a.agent_type === 'analyzer')
  )

  const healerAgents = computed(() =>
    agents.value.filter(a => a.agent_type === 'healer')
  )

  const validatorAgents = computed(() =>
    agents.value.filter(a => a.agent_type === 'validator')
  )

  const isConsensusReady = computed(() =>
    consensusStatus.value?.consensus_ready ?? false
  )

  // Actions
  async function fetchAgents(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/api/v1/agents', { params })
      agents.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchConsensusStatus() {
    try {
      const response = await api.get('/api/v1/agents/consensus/status')
      consensusStatus.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function restartAgent(agentId) {
    try {
      const response = await api.post(`/api/v1/agents/${agentId}/restart`)
      await fetchAgents()
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  function updateAgentStatus(agentId, status) {
    const agent = agents.value.find(a => a.id === agentId)
    if (agent) {
      agent.status = status
    }
  }

  return {
    agents,
    consensusStatus,
    loading,
    error,
    onlineAgents,
    analyzerAgents,
    healerAgents,
    validatorAgents,
    isConsensusReady,
    fetchAgents,
    fetchConsensusStatus,
    restartAgent,
    updateAgentStatus
  }
})
