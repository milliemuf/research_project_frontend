import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useTimelineStore = defineStore('timeline', () => {
  const events = ref([])
  const currentBugId = ref(null)
  const scrubPosition = ref(1) // 0.0–1.0
  const loading = ref(false)

  const phases = computed(() => {
    const groups = {}
    for (const e of events.value) {
      ;(groups[e.phase] ||= []).push(e)
    }
    return groups
  })

  const visibleEvents = computed(() => {
    const n = Math.max(1, Math.ceil(events.value.length * scrubPosition.value))
    return events.value.slice(0, n)
  })

  const currentEvent = computed(() => {
    const vis = visibleEvents.value
    return vis.length ? vis[vis.length - 1] : null
  })

  async function fetchTimeline(bugId) {
    loading.value = true
    currentBugId.value = bugId
    try {
      const res = await api.get(`/api/v1/timeline/${bugId}`)
      events.value = res.data
    } catch (e) {
      console.warn('timeline:', e.message)
    } finally {
      loading.value = false
    }
  }

  function setScrub(v) { scrubPosition.value = Math.max(0, Math.min(1, v)) }

  return { events, currentBugId, scrubPosition, loading, phases, visibleEvents, currentEvent, fetchTimeline, setScrub }
})
