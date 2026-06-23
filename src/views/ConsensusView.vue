<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAgentsStore } from '@/stores/agents'
import api from '@/services/api'

const agentsStore = useAgentsStore()
const rounds = ref([])
const phase = ref('pre_prepare')
const PHASES = ['pre_prepare', 'prepare', 'commit', 'reply']
const phaseLabel = { pre_prepare: 'Pre-Prepare', prepare: 'Prepare', commit: 'Commit', reply: 'Reply' }
const tickRef = ref(0)
let phaseTimer, tickTimer

onMounted(async () => {
  await agentsStore.fetchAgents()
  try { rounds.value = (await api.get('/api/v1/consensus/rounds')).data } catch {}
  // Cycle through phases for the live demo visualisation
  phaseTimer = setInterval(() => {
    const i = PHASES.indexOf(phase.value)
    phase.value = PHASES[(i + 1) % PHASES.length]
  }, 1800)
  tickTimer = setInterval(() => tickRef.value++, 60)
})
onUnmounted(() => { clearInterval(phaseTimer); clearInterval(tickTimer) })

// Layout agents in a circle. Primary at top.
const layout = computed(() => {
  const list = agentsStore.agents.length ? agentsStore.agents : []
  const n = list.length || 9
  const cx = 280, cy = 250, r = 180
  return list.map((a, i) => {
    const angle = (-Math.PI / 2) + (i / n) * Math.PI * 2
    return {
      ...a,
      x: cx + Math.cos(angle) * r,
      y: cy + Math.sin(angle) * r,
      isPrimary: i === 0,
    }
  })
})

const cx = 280, cy = 250

// Determine which agents have "voted" in the current phase (animated)
const phaseIdx = computed(() => PHASES.indexOf(phase.value))
const activeVoters = computed(() => {
  const total = layout.value.length
  if (phaseIdx.value === 0) return [layout.value[0]] // primary multicast
  // For prepare/commit, ramp up votes within the 1.8s window
  const elapsed = (tickRef.value % 30) / 30 // 0..1 within phase
  const k = Math.max(1, Math.floor(total * Math.min(1, elapsed + 0.2)))
  return layout.value.slice(0, k)
})

const requiredQuorum = computed(() => {
  const n = layout.value.length || 9
  const f = Math.floor((n - 1) / 3)
  return 2 * f + 1
})
const byzantineTolerance = computed(() => Math.floor(((layout.value.length || 9) - 1) / 3))

const successRate = computed(() => {
  if (!rounds.value.length) return 0
  return (rounds.value.filter(r => r.success).length / rounds.value.length) * 100
})

const recent = computed(() => rounds.value.slice(0, 8))

function agentColor(type) {
  return type === 'analyzer' ? '#A855F7'
       : type === 'healer'   ? '#22D3EE'
       : '#34D399'
}
</script>

<template>
  <div class="space-y-3 xl:space-y-4">
    <!-- Header strip -->
    <section class="panel px-5 py-3 flex flex-wrap items-center gap-4 justify-between">
      <div class="flex items-center gap-3">
        <span class="live-dot"></span>
        <div>
          <p class="eyebrow">Practical Byzantine Fault Tolerance</p>
          <h2 class="font-display text-lg text-ink-100 leading-tight">PBFT Consensus Monitor</h2>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <span class="tag tag-slate">N = <span class="text-ink-100">{{ layout.length || 9 }}</span></span>
        <span class="tag tag-slate">f ≤ <span class="text-ink-100">{{ byzantineTolerance }}</span></span>
        <span class="tag tag-emerald">Quorum 2f+1 = {{ requiredQuorum }}</span>
        <span class="tag tag-violet">view 0</span>
      </div>
    </section>

    <!-- Single-viewport grid: mesh + side rails + recent rounds in one row on xl+ -->
    <section class="grid grid-cols-1 xl:grid-cols-12 gap-4">
      <!-- Mesh visualization -->
      <div class="panel xl:col-span-7 overflow-hidden">
        <div class="panel-header">
          <h3 class="panel-title">Live consensus mesh · round #{{ rounds[0]?.sequence ?? '—' }}</h3>
          <div class="flex items-center gap-2">
            <span v-for="p in PHASES" :key="p"
              :class="['font-mono text-[10px] uppercase tracking-wider px-2 py-0.5 rounded',
                phase === p ? 'bg-brand-500/20 text-brand-200 ring-1 ring-brand-500/40' : 'text-ink-500']">
              {{ phaseLabel[p] }}
            </span>
          </div>
        </div>
        <div class="relative">
          <div class="absolute inset-0 bg-glow-radial pointer-events-none"></div>
          <svg viewBox="0 0 560 540" class="w-full block">
            <!-- Ring -->
            <circle :cx="cx" :cy="cy" r="180" fill="none" class="mesh-ring-a" stroke-dasharray="3 4"/>
            <circle :cx="cx" :cy="cy" r="120" fill="none" class="mesh-ring-b"/>
            <circle :cx="cx" :cy="cy" r="60"  fill="none" class="mesh-ring-b"/>

            <!-- Center digest -->
            <g>
              <circle :cx="cx" :cy="cy" r="44" class="mesh-center-bg mesh-center-ring" stroke-width="1.5"/>
              <text :x="cx" :y="cy - 6" text-anchor="middle" class="fill-ink-muted" style="font: 500 9px 'JetBrains Mono';">DIGEST</text>
              <text :x="cx" :y="cy + 8" text-anchor="middle" class="fill-ink-strong" style="font: 600 11px 'JetBrains Mono';">a3f2…91c4</text>
              <text :x="cx" :y="cy + 22" text-anchor="middle" class="fill-brand-300" style="font: 500 9px 'JetBrains Mono';">{{ phaseLabel[phase] }}</text>
            </g>

            <!-- Vote edges -->
            <g>
              <template v-for="(a, i) in layout" :key="`edge-${a.id}`">
                <line v-if="phaseIdx === 0 && a.isPrimary === false"
                  :x1="layout[0]?.x" :y1="layout[0]?.y" :x2="a.x" :y2="a.y"
                  stroke="#7C8CFF" stroke-width="1" stroke-opacity="0.5"
                  stroke-dasharray="4 4" />
                <line v-else-if="phaseIdx > 0 && activeVoters.find(v => v.id === a.id)"
                  :x1="cx" :y1="cy" :x2="a.x" :y2="a.y"
                  :stroke="agentColor(a.agent_type)" stroke-width="1.2" stroke-opacity="0.55"/>
              </template>
            </g>

            <!-- Animated vote pulses -->
            <g>
              <template v-for="(a, i) in activeVoters" :key="`pulse-${a.id}-${tickRef}`">
                <circle v-if="phaseIdx > 0"
                  :cx="cx + (a.x - cx) * (((tickRef + i*4) % 30) / 30)"
                  :cy="cy + (a.y - cy) * (((tickRef + i*4) % 30) / 30)"
                  r="3"
                  :fill="agentColor(a.agent_type)" fill-opacity="0.95"/>
              </template>
            </g>

            <!-- Agent nodes -->
            <g>
              <g v-for="(a, i) in layout" :key="`node-${a.id}`">
                <circle :cx="a.x" :cy="a.y" r="22"
                  :fill="agentColor(a.agent_type)" fill-opacity="0.15"
                  :stroke="agentColor(a.agent_type)" stroke-width="1.5"/>
                <circle v-if="a.isPrimary" :cx="a.x" :cy="a.y" r="28"
                  fill="none" stroke="#FBBF24" stroke-width="1" stroke-dasharray="2 3"
                  style="animation: tick 18s linear infinite; transform-origin: center;"/>
                <text :x="a.x" :y="a.y + 4" text-anchor="middle"
                  :fill="agentColor(a.agent_type)" style="font: 700 11px 'JetBrains Mono';">
                  {{ a.agent_type.charAt(0).toUpperCase() }}{{ (i % 3) + 1 }}
                </text>
                <text :x="a.x" :y="a.y + 38" text-anchor="middle" class="fill-ink-400" style="font: 500 9px 'JetBrains Mono';">
                  {{ a.llm_provider }}
                </text>
                <text v-if="a.isPrimary" :x="a.x" :y="a.y - 30" text-anchor="middle" class="fill-amber-300" style="font: 600 9px 'JetBrains Mono';">PRIMARY</text>
              </g>
            </g>

            <!-- Key (legend) — sits below the provider labels on a faint divider -->
            <line x1="20" y1="495" x2="540" y2="495" class="mesh-ring-b" stroke-width="1"/>
            <g transform="translate(20,520)">
              <text x="0" y="4" class="fill-ink-muted" style="font: 600 9px 'JetBrains Mono'; letter-spacing: 0.22em;">KEY</text>
              <circle cx="52"  cy="0" r="5" fill="#A855F7" fill-opacity="0.4" stroke="#A855F7"/><text x="64"  y="4" class="fill-ink-muted" style="font: 500 10px 'JetBrains Mono';">Analyzer</text>
              <circle cx="152" cy="0" r="5" fill="#22D3EE" fill-opacity="0.4" stroke="#22D3EE"/><text x="164" y="4" class="fill-ink-muted" style="font: 500 10px 'JetBrains Mono';">Healer</text>
              <circle cx="238" cy="0" r="5" fill="#34D399" fill-opacity="0.4" stroke="#34D399"/><text x="250" y="4" class="fill-ink-muted" style="font: 500 10px 'JetBrains Mono';">Validator</text>
            </g>
          </svg>
        </div>
      </div>

      <!-- Side rails: phase ladder + metrics -->
      <div class="xl:col-span-3 space-y-4">
        <!-- Phase ladder -->
        <div class="panel">
          <div class="panel-header py-2"><h3 class="panel-title">PBFT phase ladder</h3></div>
          <div class="p-3 space-y-1.5">
            <div v-for="(p, i) in PHASES" :key="p"
              class="flex items-start gap-2.5 p-2 rounded-lg border border-white/5 transition"
              :class="phase === p ? 'bg-brand-500/10 border-brand-500/30' : 'bg-ink-850/40'">
              <div :class="['w-6 h-6 rounded-md flex items-center justify-center font-mono text-[10px] font-bold shrink-0',
                phase === p ? 'bg-brand-500 text-white' :
                PHASES.indexOf(phase) > i ? 'bg-emerald-500/20 text-emerald-300' : 'bg-white/5 text-ink-400']">
                {{ i + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-[11.5px] text-ink-100 font-medium leading-tight">{{ phaseLabel[p] }}</p>
                <p class="font-mono text-[10px] text-ink-400 leading-snug mt-0.5 line-clamp-2">
                  <template v-if="p === 'pre_prepare'">Primary multicasts PRE-PREPARE with proposed fix.</template>
                  <template v-else-if="p === 'prepare'">Replicas validate &amp; broadcast PREPARE. Wait for 2f matching.</template>
                  <template v-else-if="p === 'commit'">On 2f+1 prepares, broadcast COMMIT. Wait for 2f+1 commits.</template>
                  <template v-else>Apply fix to sandbox; primary replies. State advances.</template>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Live counters -->
        <div class="panel">
          <div class="panel-header py-2"><h3 class="panel-title">Round metrics</h3></div>
          <div class="p-3 grid grid-cols-2 gap-2">
            <div class="panel-quiet p-2.5">
              <p class="eyebrow">Total</p>
              <p class="font-display text-xl text-ink-100 mt-0.5">{{ rounds.length }}</p>
            </div>
            <div class="panel-quiet p-2.5">
              <p class="eyebrow">Success</p>
              <p class="font-display text-xl text-emerald-300 mt-0.5">{{ successRate.toFixed(1) }}%</p>
            </div>
            <div class="panel-quiet p-2.5">
              <p class="eyebrow">View Δ</p>
              <p class="font-display text-xl text-amber-300 mt-0.5">{{ rounds.filter(r => r.reason === 'view_change').length }}</p>
            </div>
            <div class="panel-quiet p-2.5">
              <p class="eyebrow">Byzantine</p>
              <p class="font-display text-xl text-rose-300 mt-0.5">{{ rounds.filter(r => r.reason === 'byzantine_detected').length }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent rounds — compact list replaces the long table so it fits in-view -->
      <div class="panel xl:col-span-2 overflow-hidden">
        <div class="panel-header py-2">
          <h3 class="panel-title">Recent rounds</h3>
          <span class="font-mono text-[10px] text-ink-400">{{ rounds.length }}</span>
        </div>
        <ul v-if="recent.length" class="divide-y divide-white/5">
          <li v-for="r in recent.slice(0, 8)" :key="r.id"
              class="px-3 py-2 hover:bg-white/[0.02] transition">
            <div class="flex items-center justify-between gap-2">
              <span class="font-mono text-[11px] text-ink-300">#{{ r.sequence }}</span>
              <span v-if="r.success" class="status status-resolved !px-1.5 !py-0.5 !text-[9px]">ok</span>
              <span v-else class="status status-failed !px-1.5 !py-0.5 !text-[9px]">{{ r.reason === 'view_change' ? 'view Δ' : 'fail' }}</span>
            </div>
            <p class="font-mono text-[10px] text-ink-400 truncate mt-0.5">{{ r.bug_id }}</p>
            <div class="flex items-center gap-3 mt-1 font-mono text-[10px]">
              <span><span class="text-cyan-300">{{ r.prepares.length }}</span><span class="text-ink-500">/{{ requiredQuorum }}</span> P</span>
              <span><span class="text-emerald-300">{{ r.commits.length }}</span><span class="text-ink-500">/{{ requiredQuorum }}</span> C</span>
              <span class="text-ink-400 ml-auto">{{ r.durationMs >= 1000 ? (r.durationMs / 1000).toFixed(0) + 's' : r.durationMs + 'ms' }}</span>
            </div>
          </li>
        </ul>
        <div v-else class="p-4 text-center text-ink-400 text-[11px]">No rounds yet</div>
      </div>
    </section>
  </div>
</template>
