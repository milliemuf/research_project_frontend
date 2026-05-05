<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useTimelineStore } from '@/stores/timeline'
import { useBugsStore } from '@/stores/bugs'

const route = useRoute()
const tl = useTimelineStore()
const bugsStore = useBugsStore()

const scrubPct = ref(100)

const PHASE_META = {
  detection:  { color: '#60A5FA', label: 'Detection' },
  analysis:   { color: '#A855F7', label: 'Analysis' },
  healing:    { color: '#22D3EE', label: 'Healing' },
  validation: { color: '#34D399', label: 'Validation' },
  consensus:  { color: '#F59E0B', label: 'Consensus' },
  applied:    { color: '#7C8CFF', label: 'Applied' },
}
const PHASES = Object.keys(PHASE_META)

function agentBadge(type) {
  return type === 'analyzer' ? 'bg-agent-analyzer'
       : type === 'healer'   ? 'bg-agent-healer'
       : type === 'system'   ? 'bg-brand-500'
       :                       'bg-agent-validator'
}

onMounted(async () => {
  await bugsStore.fetchBugs().catch(() => {})
  const bugId = route.params.bugId || bugsStore.bugs[0]?.id || 'bug-0001'
  await tl.fetchTimeline(bugId)
})

watch(scrubPct, (v) => tl.setScrub(v / 100))

const svgW = 960, svgH = 140, padX = 40, lineY = 70
const nodePositions = computed(() => {
  const evts = tl.events
  if (!evts.length) return []
  const times = evts.map(e => new Date(e.timestamp).getTime())
  const t0 = Math.min(...times), t1 = Math.max(...times)
  const span = t1 - t0 || 1
  return evts.map((e, i) => ({
    ...e, _i: i,
    cx: padX + ((times[i] - t0) / span) * (svgW - 2 * padX),
    cy: lineY,
  }))
})

const phaseRegions = computed(() => {
  if (!nodePositions.value.length) return []
  const regions = []
  let cur = null
  for (const n of nodePositions.value) {
    if (!cur || cur.phase !== n.phase) {
      if (cur) cur.x2 = n.cx
      cur = { phase: n.phase, x1: n.cx, x2: n.cx }
      regions.push(cur)
    } else { cur.x2 = n.cx }
  }
  return regions
})

const visibleCount = computed(() => tl.visibleEvents.length)

const fmtTime = (ts) => new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <section class="panel px-5 py-3 flex flex-wrap items-center gap-4 justify-between">
      <div>
        <p class="eyebrow">Repair lifecycle replay</p>
        <h2 class="font-display text-lg text-ink-100">Bug {{ tl.currentBugId }}</h2>
      </div>
      <div class="flex items-center gap-2">
        <span v-for="p in PHASES" :key="p"
          class="tag" :style="{ backgroundColor: PHASE_META[p].color + '18', color: PHASE_META[p].color, boxShadow: '0 0 0 1px ' + PHASE_META[p].color + '50' }">
          {{ PHASE_META[p].label }}
        </span>
      </div>
    </section>

    <!-- SVG timeline -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Event timeline · {{ tl.events.length }} events</h3>
        <span class="font-mono text-[11px] text-ink-400">scrub {{ scrubPct }}%</span>
      </div>
      <div class="panel-body">
        <svg :viewBox="`0 0 ${svgW} ${svgH}`" class="w-full block" style="min-height: 120px">
          <!-- Phase regions -->
          <rect v-for="(r, i) in phaseRegions" :key="'r'+i"
            :x="r.x1 - 8" :y="10" :width="r.x2 - r.x1 + 16" :height="svgH - 20" rx="8"
            :fill="PHASE_META[r.phase]?.color || '#7C8CFF'" fill-opacity="0.06"/>

          <!-- Main axis -->
          <line :x1="padX" :y1="lineY" :x2="svgW - padX" :y2="lineY" class="mesh-ring-a" stroke-width="2"/>

          <!-- Scrub position line -->
          <line v-if="nodePositions.length"
            :x1="nodePositions[visibleCount - 1]?.cx || padX" :y1="10"
            :x2="nodePositions[visibleCount - 1]?.cx || padX" :y2="svgH - 10"
            stroke="#7C8CFF" stroke-width="1.5" stroke-dasharray="4 3" stroke-opacity="0.7"/>

          <!-- Event nodes -->
          <g v-for="(n, i) in nodePositions" :key="n.id">
            <circle :cx="n.cx" :cy="n.cy" :r="i < visibleCount ? 8 : 5"
              :fill="PHASE_META[n.phase]?.color || '#7C8CFF'"
              :fill-opacity="i < visibleCount ? 0.85 : 0.15"
              :stroke="PHASE_META[n.phase]?.color || '#7C8CFF'" stroke-width="1.5"
              :stroke-opacity="i < visibleCount ? 1 : 0.3"/>
            <!-- Vote badge -->
            <text v-if="n.vote && i < visibleCount"
              :x="n.cx" :y="n.cy + 3" text-anchor="middle"
              :fill="n.vote === 'veto' ? '#FB7185' : '#fff'" style="font: 700 8px 'JetBrains Mono';">
              {{ n.vote === 'prepare' ? 'P' : n.vote === 'commit' ? 'C' : '!' }}
            </text>
            <!-- Agent label below -->
            <text :x="n.cx" :y="n.cy + 22" text-anchor="middle" class="fill-ink-muted" style="font: 500 8px 'JetBrains Mono';"
              :fill-opacity="i < visibleCount ? 0.8 : 0.25">
              {{ n.agent_id.split('-')[0]?.slice(0,3) }}
            </text>
          </g>
        </svg>
        <input type="range" min="1" max="100" v-model.number="scrubPct" class="scrub-slider mt-2"/>
      </div>
    </section>

    <!-- Event cards -->
    <section class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
      <transition-group name="page">
        <div v-for="evt in tl.visibleEvents" :key="evt.id"
          class="panel-quiet p-4 space-y-1.5"
          :class="evt.vote === 'veto' ? 'ring-1 ring-rose-500/30' : ''">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div :class="['w-6 h-6 rounded-md flex items-center justify-center text-[10px] font-mono font-bold text-white', agentBadge(evt.agent_type)]">
                {{ evt.agent_type.charAt(0).toUpperCase() }}
              </div>
              <span class="font-mono text-[11px] text-ink-300">{{ evt.agent_id }}</span>
            </div>
            <span class="tag text-[9px]" :style="{ backgroundColor: PHASE_META[evt.phase]?.color + '18', color: PHASE_META[evt.phase]?.color }">
              {{ PHASE_META[evt.phase]?.label }}
            </span>
          </div>
          <p class="text-[12.5px] text-ink-100 font-medium">{{ evt.action }}</p>
          <p v-if="evt.detail" class="font-mono text-[10.5px] text-ink-400 leading-snug">{{ evt.detail }}</p>
          <div class="flex items-center justify-between font-mono text-[10px] text-ink-500 pt-1">
            <span>{{ evt.duration_ms }}ms</span>
            <span>{{ fmtTime(evt.timestamp) }}</span>
          </div>
        </div>
      </transition-group>
    </section>
  </div>
</template>
