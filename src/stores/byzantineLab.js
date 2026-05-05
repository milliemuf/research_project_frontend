import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useByzantineLabStore = defineStore('byzantineLab', () => {
  const agents = ref([])
  const results = ref([])
  const running = ref(false)
  const summary = ref({ total_runs: 0, survived: 0, failed: 0, survival_rate: 0 })

  async function fetchHistory() {
    try {
      const res = await api.get('/api/v1/byzantine')
      agents.value = res.data.agents
      results.value = res.data.scenarios
      summary.value = res.data.summary
    } catch (e) {
      console.warn('byzantine:', e.message)
    }
  }

  function toggleFault(agentId, faultType) {
    const a = agents.value.find(x => x.id === agentId)
    if (!a) return
    if (a.fault_injected && a.fault_type === faultType) {
      a.fault_injected = false
      a.fault_type = null
    } else {
      a.fault_injected = true
      a.fault_type = faultType
    }
  }

  async function runScenario() {
    running.value = true
    const faults = agents.value.filter(a => a.fault_injected).map(a => ({
      agent_id: a.id, fault_type: a.fault_type,
    }))
    const n = agents.value.length || 9
    const maxFaults = Math.floor((n - 1) / 3)
    await new Promise(r => setTimeout(r, 800 + Math.random() * 600))
    const survived = faults.length <= maxFaults ? Math.random() > 0.08 : Math.random() > 0.75
    const result = {
      id: `scenario-${(results.value.length + 1).toString().padStart(3, '0')}`,
      faults,
      survived,
      rounds_to_recover: survived ? Math.floor(Math.random() * 4) + 1 : 0,
      consensus_achieved: survived,
      duration_ms: 180 + Math.floor(Math.random() * 500),
      log: [
        `Injected ${faults.length} fault(s): ${faults.map(f => f.fault_type.replace(/_/g, ' ')).join(', ') || 'none'}`,
        survived ? 'View change triggered — new primary elected' : 'Consensus timeout — system halted',
        survived ? `Recovery in ${Math.floor(Math.random() * 4) + 1} round(s)` : 'Manual intervention required',
      ],
    }
    results.value.unshift(result)
    summary.value.total_runs++
    if (survived) summary.value.survived++
    else summary.value.failed++
    summary.value.survival_rate = +(summary.value.survived / summary.value.total_runs).toFixed(3)
    running.value = false
  }

  return { agents, results, running, summary, fetchHistory, toggleFault, runScenario }
})
