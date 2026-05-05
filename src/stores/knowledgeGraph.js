import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useKnowledgeGraphStore = defineStore('knowledgeGraph', () => {
  const nodes = ref([])
  const edges = ref([])
  const selectedNodeId = ref(null)
  const loading = ref(false)

  const selectedNode = computed(() =>
    nodes.value.find(n => n.id === selectedNodeId.value) || null
  )

  const connectedEdges = computed(() => {
    if (!selectedNodeId.value) return []
    return edges.value.filter(e => e.source === selectedNodeId.value || e.target === selectedNodeId.value)
  })

  const connectedNodes = computed(() => {
    const ids = new Set()
    for (const e of connectedEdges.value) {
      ids.add(e.source === selectedNodeId.value ? e.target : e.source)
    }
    return nodes.value.filter(n => ids.has(n.id))
  })

  async function fetchGraph() {
    loading.value = true
    try {
      const res = await api.get('/api/v1/knowledge-graph')
      nodes.value = res.data.nodes
      edges.value = res.data.edges
    } catch (e) {
      console.warn('knowledge-graph:', e.message)
    } finally {
      loading.value = false
    }
  }

  function selectNode(id) { selectedNodeId.value = id === selectedNodeId.value ? null : id }
  function updateNodePosition(id, x, y) {
    const n = nodes.value.find(n => n.id === id)
    if (n) { n.x = x; n.y = y }
  }

  return { nodes, edges, selectedNodeId, selectedNode, connectedEdges, connectedNodes, loading, fetchGraph, selectNode, updateNodePosition }
})
