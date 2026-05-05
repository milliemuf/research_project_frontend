<script setup>
import { ref, computed, onMounted } from 'vue'
import { useKnowledgeGraphStore } from '@/stores/knowledgeGraph'

const graph = useKnowledgeGraphStore()
const dragging = ref(null)
const svgRef = ref(null)

onMounted(() => graph.fetchGraph())

const NODE_META = {
  bug:     { color: '#FB7185', r: 14, tag: 'tag-rose' },
  pattern: { color: '#A78BFA', r: 18, tag: 'tag-violet' },
  fix:     { color: '#34D399', r: 12, tag: 'tag-emerald' },
}

function nodeColor(n) { return NODE_META[n.type]?.color || '#7C8CFF' }
function nodeR(n) { return NODE_META[n.type]?.r || 14 }

function edgeColor(e) {
  return e.relation === 'exhibits' ? 'rgba(251,113,133,0.2)'
       : e.relation === 'resolved_by' ? 'rgba(52,211,153,0.25)'
       : 'rgba(167,139,250,0.15)'
}

function getNodeById(id) { return graph.nodes.find(n => n.id === id) }

function svgPoint(evt) {
  const svg = svgRef.value
  if (!svg) return { x: 0, y: 0 }
  const pt = svg.createSVGPoint()
  pt.x = evt.clientX; pt.y = evt.clientY
  const ctm = svg.getScreenCTM()?.inverse()
  if (!ctm) return { x: 0, y: 0 }
  const svgP = pt.matrixTransform(ctm)
  return { x: svgP.x, y: svgP.y }
}

function startDrag(node, evt) {
  evt.preventDefault()
  dragging.value = node.id
}

function onMove(evt) {
  if (!dragging.value) return
  const p = svgPoint(evt)
  graph.updateNodePosition(dragging.value, p.x, p.y)
}

function stopDrag() { dragging.value = null }

const relationLabel = { exhibits: 'Exhibits', resolved_by: 'Resolved by', similar_to: 'Similar to' }
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <section class="panel px-5 py-3 flex flex-wrap items-center gap-4 justify-between">
      <div>
        <p class="eyebrow">Bug pattern learning</p>
        <h2 class="font-display text-lg text-ink-100">Knowledge Graph Explorer</h2>
      </div>
      <div class="flex items-center gap-2">
        <span class="tag tag-rose">Bug</span>
        <span class="tag tag-violet">Pattern</span>
        <span class="tag tag-emerald">Fix</span>
        <span class="tag tag-slate">{{ graph.nodes.length }} nodes · {{ graph.edges.length }} edges</span>
      </div>
    </section>

    <section class="grid grid-cols-1 xl:grid-cols-12 gap-4">
      <!-- Graph SVG -->
      <div class="panel xl:col-span-8 overflow-hidden">
        <div class="panel-header"><h3 class="panel-title">Force-directed graph</h3></div>
        <div class="relative">
          <div class="absolute inset-0 bg-glow-radial pointer-events-none"></div>
          <svg ref="svgRef" viewBox="0 0 800 600" class="w-full block" style="min-height: 480px"
               @mousemove="onMove" @mouseup="stopDrag" @mouseleave="stopDrag">
            <!-- Edges -->
            <line v-for="(e, i) in graph.edges" :key="'e'+i"
              :x1="getNodeById(e.source)?.x || 0" :y1="getNodeById(e.source)?.y || 0"
              :x2="getNodeById(e.target)?.x || 0" :y2="getNodeById(e.target)?.y || 0"
              :stroke="edgeColor(e)" stroke-width="1.5"
              :stroke-opacity="graph.selectedNodeId && (e.source === graph.selectedNodeId || e.target === graph.selectedNodeId) ? 1 : 0.5"
              :stroke-width="graph.selectedNodeId && (e.source === graph.selectedNodeId || e.target === graph.selectedNodeId) ? 2.5 : 1.5"/>

            <!-- Nodes -->
            <g v-for="n in graph.nodes" :key="n.id" class="graph-node"
               @mousedown.stop="startDrag(n, $event)"
               @click.stop="graph.selectNode(n.id)">
              <!-- Selection glow -->
              <circle v-if="graph.selectedNodeId === n.id"
                :cx="n.x" :cy="n.y" :r="nodeR(n) + 6"
                fill="none" :stroke="nodeColor(n)" stroke-width="1.5" stroke-dasharray="3 2" stroke-opacity="0.6"/>
              <circle :cx="n.x" :cy="n.y" :r="nodeR(n)"
                :fill="nodeColor(n)" fill-opacity="0.2"
                :stroke="nodeColor(n)" stroke-width="1.5"/>
              <text :x="n.x" :y="n.y + 4" text-anchor="middle" fill="white"
                style="font: 700 9px 'JetBrains Mono'; pointer-events: none;">
                {{ n.type === 'bug' ? 'B' : n.type === 'pattern' ? 'P' : 'F' }}
              </text>
              <text :x="n.x" :y="n.y + nodeR(n) + 13" text-anchor="middle" class="fill-ink-muted"
                style="font: 500 8px 'JetBrains Mono'; pointer-events: none;">
                {{ n.label.length > 16 ? n.label.slice(0,14) + '…' : n.label }}
              </text>
            </g>
          </svg>
        </div>
      </div>

      <!-- Detail panel -->
      <div class="xl:col-span-4 space-y-4">
        <div v-if="graph.selectedNode" class="panel">
          <div class="panel-header">
            <h3 class="panel-title">{{ graph.selectedNode.type }} detail</h3>
            <span :class="NODE_META[graph.selectedNode.type]?.tag || 'tag-slate'" class="tag">{{ graph.selectedNode.type }}</span>
          </div>
          <div class="panel-body space-y-3">
            <div>
              <p class="eyebrow">Label</p>
              <p class="text-[13px] text-ink-100 mt-0.5">{{ graph.selectedNode.label }}</p>
            </div>
            <div>
              <p class="eyebrow">ID</p>
              <p class="font-mono text-[11px] text-ink-300 mt-0.5">{{ graph.selectedNode.id }}</p>
            </div>
            <div v-if="graph.selectedNode.severity">
              <p class="eyebrow">Severity</p>
              <span :class="`sev-${graph.selectedNode.severity}`">{{ graph.selectedNode.severity }}</span>
            </div>
            <div v-if="graph.selectedNode.success_rate != null">
              <p class="eyebrow">Success rate</p>
              <p class="font-display text-xl text-emerald-300 mt-0.5">{{ (graph.selectedNode.success_rate * 100).toFixed(1) }}%</p>
            </div>
            <div>
              <p class="eyebrow">Connections ({{ graph.connectedNodes.length }})</p>
              <ul class="mt-1 space-y-1">
                <li v-for="cn in graph.connectedNodes" :key="cn.id"
                  class="flex items-center gap-2 text-[11px] cursor-pointer hover:text-ink-100 transition"
                  @click="graph.selectNode(cn.id)">
                  <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: nodeColor(cn) }"></span>
                  <span class="text-ink-300">{{ cn.label }}</span>
                  <span class="font-mono text-[9px] text-ink-500">{{ cn.type }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div v-else class="panel">
          <div class="panel-body text-center py-12 text-ink-400 text-[12px]">
            Click a node to inspect its details and connections
          </div>
        </div>

        <!-- Relations legend -->
        <div class="panel">
          <div class="panel-header"><h3 class="panel-title">Edge types</h3></div>
          <div class="panel-body space-y-2">
            <div v-for="(lbl, rel) in relationLabel" :key="rel" class="flex items-center gap-2">
              <span class="w-6 h-0.5 rounded" :style="{ backgroundColor: edgeColor({ relation: rel }).replace(/[\d.]+\)$/, '0.8)') }"></span>
              <span class="font-mono text-[10px] text-ink-300">{{ lbl }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
