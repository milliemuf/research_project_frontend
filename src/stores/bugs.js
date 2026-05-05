import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useBugsStore = defineStore('bugs', () => {
  // State
  const bugs = ref([])
  const currentBug = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const stats = ref(null)

  // Getters
  const activeBugs = computed(() =>
    bugs.value.filter(b => !['resolved', 'failed'].includes(b.status))
  )

  const resolvedBugs = computed(() =>
    bugs.value.filter(b => b.status === 'resolved')
  )

  const criticalBugs = computed(() =>
    bugs.value.filter(b => b.severity === 'critical')
  )

  // Actions
  async function fetchBugs(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/api/v1/bugs', { params })
      bugs.value = response.data.bugs
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchBug(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/api/v1/bugs/${id}`)
      currentBug.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    try {
      const response = await api.get('/api/v1/bugs/stats/summary')
      stats.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  function addBug(bug) {
    bugs.value.unshift(bug)
  }

  function updateBug(updatedBug) {
    const index = bugs.value.findIndex(b => b.id === updatedBug.id)
    if (index !== -1) {
      bugs.value[index] = updatedBug
    }
    if (currentBug.value?.id === updatedBug.id) {
      currentBug.value = updatedBug
    }
  }

  return {
    bugs,
    currentBug,
    loading,
    error,
    stats,
    activeBugs,
    resolvedBugs,
    criticalBugs,
    fetchBugs,
    fetchBug,
    fetchStats,
    addBug,
    updateBug
  }
})
