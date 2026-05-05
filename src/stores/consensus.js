import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useConsensusStore = defineStore('consensus', () => {
  // State
  const activeRounds = ref([])
  const completedRounds = ref([])
  const currentRound = ref(null)

  // Getters
  const totalRounds = computed(() =>
    activeRounds.value.length + completedRounds.value.length
  )

  const successRate = computed(() => {
    if (completedRounds.value.length === 0) return 0
    const successful = completedRounds.value.filter(r => r.success).length
    return (successful / completedRounds.value.length) * 100
  })

  // Actions
  function startRound(roundData) {
    currentRound.value = {
      ...roundData,
      phase: 'pre_prepare',
      prepares: [],
      commits: [],
      startedAt: new Date().toISOString()
    }
    activeRounds.value.push(currentRound.value)
  }

  function updateRoundPhase(roundId, phase, data = {}) {
    const round = activeRounds.value.find(r => r.id === roundId)
    if (round) {
      round.phase = phase
      Object.assign(round, data)
    }
    if (currentRound.value?.id === roundId) {
      currentRound.value.phase = phase
      Object.assign(currentRound.value, data)
    }
  }

  function addPrepareVote(roundId, vote) {
    const round = activeRounds.value.find(r => r.id === roundId)
    if (round) {
      round.prepares.push(vote)
    }
  }

  function addCommitVote(roundId, vote) {
    const round = activeRounds.value.find(r => r.id === roundId)
    if (round) {
      round.commits.push(vote)
    }
  }

  function completeRound(roundId, success, reason) {
    const index = activeRounds.value.findIndex(r => r.id === roundId)
    if (index !== -1) {
      const round = activeRounds.value.splice(index, 1)[0]
      round.success = success
      round.reason = reason
      round.completedAt = new Date().toISOString()
      completedRounds.value.unshift(round)

      if (currentRound.value?.id === roundId) {
        currentRound.value = null
      }
    }
  }

  function clearCompleted() {
    completedRounds.value = []
  }

  return {
    activeRounds,
    completedRounds,
    currentRound,
    totalRounds,
    successRate,
    startRound,
    updateRoundPhase,
    addPrepareVote,
    addCommitVote,
    completeRound,
    clearCompleted
  }
})
