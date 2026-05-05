<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const data = ref(null)
const hoveredCell = ref(null)

onMounted(() => {
  api.get('/api/v1/heatmap').then(r => { data.value = r.data }).catch(e => console.warn('heatmap:', e.message))
})

const cellSize = 48, pad = 120
const svgSize = computed(() => data.value ? pad + data.value.agents.length * cellSize + 20 : 400)

function shortId(id) {
  const parts = id.split('-')
  return parts[0].slice(0, 3).toUpperCase() + '-' + (parts[1]?.slice(0, 3) || '')
}

function cellColor(val) {
  // Interpolate: 0=rose, 0.5=ink, 1=emerald
  if (val >= 0.6) {
    const t = (val - 0.6) / 0.4
    const r = Math.round(52 + (0 - 52) * t * 0.3)
    const g = Math.round(211 * t * 0.9 + 100 * (1 - t))
    const b = Math.round(153 * t * 0.8 + 139 * (1 - t))
    return `rgba(${r},${g},${b},${0.25 + t * 0.55})`
  }
  const t = val / 0.6
  const r2 = Math.round(244 * (1 - t) + 100 * t)
  const g2 = Math.round(63 * (1 - t) + 116 * t)
  const b2 = Math.round(94 * (1 - t) + 139 * t)
  return `rgba(${r2},${g2},${b2},${0.2 + t * 0.2})`
}

const topCorrelated = computed(() => data.value?.correlations.slice(0, 5) || [])
const bottomCorrelated = computed(() => data.value?.correlations.slice(-5).reverse() || [])
</script>

<template>
  <div class="space-y-4">
    <section class="panel px-5 py-3 flex flex-wrap items-center gap-4 justify-between">
      <div>
        <p class="eyebrow">Agent diversity analysis</p>
        <h2 class="font-display text-lg text-ink-100">Consensus Agreement Heatmap</h2>
      </div>
      <span v-if="data" class="tag tag-slate">{{ data.rounds_analyzed }} rounds analyzed</span>
    </section>

    <section v-if="data" class="grid grid-cols-1 xl:grid-cols-12 gap-4">
      <!-- Heatmap -->
      <div class="panel xl:col-span-8 overflow-x-auto">
        <div class="panel-header"><h3 class="panel-title">Agreement matrix</h3></div>
        <div class="panel-body relative">
          <svg :viewBox="`0 0 ${svgSize} ${svgSize}`" class="w-full block" style="min-height: 420px">
            <!-- Column headers -->
            <text v-for="(a, j) in data.agents" :key="'ch'+j"
              :x="pad + j * cellSize + cellSize / 2" :y="pad - 8"
              text-anchor="end" class="fill-ink-muted"
              :transform="`rotate(-45, ${pad + j * cellSize + cellSize / 2}, ${pad - 8})`"
              style="font: 500 9px 'JetBrains Mono';">
              {{ shortId(a) }}
            </text>

            <!-- Row headers -->
            <text v-for="(a, i) in data.agents" :key="'rh'+i"
              :x="pad - 8" :y="pad + i * cellSize + cellSize / 2 + 4"
              text-anchor="end" class="fill-ink-muted"
              style="font: 500 9px 'JetBrains Mono';">
              {{ shortId(a) }}
            </text>

            <!-- Cells -->
            <g v-for="(row, i) in data.matrix" :key="'row'+i">
              <rect v-for="(val, j) in row" :key="'c'+i+'-'+j"
                class="heatmap-cell"
                :x="pad + j * cellSize + 1" :y="pad + i * cellSize + 1"
                :width="cellSize - 2" :height="cellSize - 2" rx="6"
                :fill="cellColor(val)"
                :stroke="i === j ? 'rgba(124,140,255,0.5)' : 'transparent'" stroke-width="1.5"
                @mouseenter="hoveredCell = { i, j, val }"
                @mouseleave="hoveredCell = null"/>
              <text v-for="(val, j) in row" :key="'t'+i+'-'+j"
                :x="pad + j * cellSize + cellSize / 2" :y="pad + i * cellSize + cellSize / 2 + 4"
                text-anchor="middle" class="fill-ink-strong pointer-events-none"
                style="font: 600 10px 'JetBrains Mono';">
                {{ i === j ? '—' : (val * 100).toFixed(0) }}
              </text>
            </g>
          </svg>

          <!-- Hover tooltip -->
          <div v-if="hoveredCell" class="absolute top-4 right-4 panel-quiet p-3 space-y-1 min-w-[160px]">
            <p class="eyebrow">Cell {{ shortId(data.agents[hoveredCell.i]) }} × {{ shortId(data.agents[hoveredCell.j]) }}</p>
            <p class="font-display text-2xl text-ink-100">{{ (hoveredCell.val * 100).toFixed(1) }}%</p>
            <p class="font-mono text-[10px] text-ink-400">agreement frequency</p>
          </div>
        </div>
      </div>

      <!-- Stats sidebar -->
      <div class="xl:col-span-4 space-y-4">
        <div class="panel">
          <div class="panel-header"><h3 class="panel-title">Most correlated</h3></div>
          <div class="panel-body space-y-2">
            <div v-for="c in topCorrelated" :key="c.agent_a+c.agent_b" class="flex items-center gap-2">
              <span class="font-mono text-[10px] text-ink-300 w-24 truncate">{{ shortId(c.agent_a) }}</span>
              <div class="flex-1 bar-track">
                <div class="bar-fill bg-gradient-to-r from-emerald-400 to-emerald-600" :style="{ width: c.agreement_pct + '%' }"></div>
              </div>
              <span class="font-mono text-[11px] text-emerald-300 w-12 text-right">{{ c.agreement_pct }}%</span>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header"><h3 class="panel-title">Least correlated</h3></div>
          <div class="panel-body space-y-2">
            <div v-for="c in bottomCorrelated" :key="c.agent_a+c.agent_b" class="flex items-center gap-2">
              <span class="font-mono text-[10px] text-ink-300 w-24 truncate">{{ shortId(c.agent_a) }}</span>
              <div class="flex-1 bar-track">
                <div class="bar-fill bg-gradient-to-r from-rose-400 to-rose-600" :style="{ width: c.agreement_pct + '%' }"></div>
              </div>
              <span class="font-mono text-[11px] text-rose-300 w-12 text-right">{{ c.agreement_pct }}%</span>
            </div>
          </div>
        </div>

        <!-- Color scale -->
        <div class="panel">
          <div class="panel-header"><h3 class="panel-title">Color scale</h3></div>
          <div class="panel-body space-y-2">
            <div class="h-4 rounded-full overflow-hidden flex">
              <div v-for="i in 20" :key="i" class="flex-1" :style="{ backgroundColor: cellColor(i / 20) }"></div>
            </div>
            <div class="flex justify-between font-mono text-[10px] text-ink-400">
              <span>0% low</span><span>50%</span><span>100% high</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
