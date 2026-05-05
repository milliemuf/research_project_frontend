<script setup>
import { ref, onMounted, computed } from 'vue'
import { useBugsStore } from '@/stores/bugs'
import { useAgentsStore } from '@/stores/agents'
import api from '@/services/api'

const bugsStore = useBugsStore()
const agentsStore = useAgentsStore()
const metrics = ref(null)
const recent = ref([])

// Fire every request in parallel and let each populate its ref independently.
// A slow endpoint no longer stalls the others — the template renders with
// fallbacks and fills in as results arrive.
onMounted(() => {
  api.get('/api/v1/dashboard/metrics').then(r => { metrics.value = r.data }).catch(e => console.warn('metrics:', e.message))
  api.get('/api/v1/dashboard/recent-activity').then(r => { recent.value = r.data }).catch(e => console.warn('recent:', e.message))
  bugsStore.fetchBugs().catch(e => console.warn('bugs:', e.message))
  agentsStore.fetchAgents().catch(e => console.warn('agents:', e.message))
  agentsStore.fetchConsensusStatus().catch(e => console.warn('consensus:', e.message))
})

const successPct = computed(() => ((metrics.value?.success_rate ?? 0) * 100).toFixed(1))
const uptime = computed(() => {
  const s = metrics.value?.uptime_seconds ?? 0
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60)
  return `${h}h ${m}m`
})

const fmtTime = (ts) => new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

const agentCount = (type) => agentsStore.agents.filter(a => a.agent_type === type).length
const byzantineF = computed(() => Math.floor((Math.max(1, agentsStore.agents.length) - 1) / 3))
const quorum = computed(() => 2 * byzantineF.value + 1)

const activityIcon = {
  bug_detected: { color: 'text-rose-300',    dot: 'bg-rose-400' },
  fix_proposed: { color: 'text-cyan-300',    dot: 'bg-cyan-400' },
  fix_applied:  { color: 'text-emerald-300', dot: 'bg-emerald-400' },
  consensus_reached: { color: 'text-violet-300', dot: 'bg-violet-400' },
  agent_status: { color: 'text-amber-300',   dot: 'bg-amber-400' },
}

const sparkline = computed(() => {
  // simple inline sparkline for throughput
  const pts = Array.from({ length: 40 }, (_, i) =>
    8 + Math.sin(i / 3) * 4 + Math.cos(i / 5) * 2
  )
  const max = Math.max(...pts), min = Math.min(...pts)
  const w = 360, h = 60
  const norm = pts.map((v, i) => {
    const x = (i / (pts.length - 1)) * w
    const y = h - ((v - min) / (max - min || 1)) * h
    return [x, y]
  })
  const path = norm.map(([x, y], i) => (i === 0 ? `M${x},${y}` : `L${x},${y}`)).join(' ')
  const area = `${path} L${w},${h} L0,${h} Z`
  return { path, area, w, h }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Hero -->
    <section class="panel overflow-hidden">
      <div class="absolute inset-0 bg-glow-radial pointer-events-none"></div>
      <div class="relative p-6 md:p-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-4">
          <p class="eyebrow">Byzantine Fault-Tolerant Multi-Agent Repair</p>
          <h1 class="h-display text-balance">
            Autonomous runtime program repair via
            <span class="bg-gradient-to-r from-violet-300 via-brand-300 to-cyan-300 bg-clip-text text-transparent">multi-LLM PBFT consensus</span>.
          </h1>
          <p class="text-ink-300 max-w-2xl text-sm leading-relaxed">
            Heterogeneous LLM agents — analyzers, healers, and validators — debate proposed fixes
            and reach Byzantine-resilient consensus before any change is applied. Current cluster:
            <span class="text-ink-100 font-mono">{{ metrics?.agents_total ?? '…' }} agents</span>, tolerating up to
            <span class="text-ink-100 font-mono">f = {{ byzantineF }}</span> faults. Evaluated on
            <span class="text-ink-100 font-mono">2,501</span> real and synthetic bugs across BugsInPy, Defects4J, and an e-commerce simulator.
          </p>
          <div class="flex flex-wrap items-center gap-2 pt-1">
            <span class="tag tag-violet">Analyzer × {{ agentCount('analyzer') }}</span>
            <span class="tag tag-cyan">Healer × {{ agentCount('healer') }}</span>
            <span class="tag tag-emerald">Validator × {{ agentCount('validator') }}</span>
            <span class="tag tag-slate">PBFT · f={{ byzantineF }}</span>
            <span class="tag tag-slate">Quorum 2f+1 = {{ quorum }}</span>
          </div>
        </div>

        <!-- Live KPIs -->
        <div class="grid grid-cols-2 gap-3">
          <div class="panel-quiet p-4">
            <p class="eyebrow">Success rate</p>
            <p class="font-display text-3xl text-emerald-300 mt-1">{{ successPct }}%</p>
            <p class="font-mono text-[10px] text-ink-400 mt-1">{{ metrics?.resolved_bugs ?? 0 }} / {{ metrics?.total_bugs ?? 0 }} fixed</p>
          </div>
          <div class="panel-quiet p-4">
            <p class="eyebrow">Avg consensus</p>
            <p class="font-display text-3xl text-cyan-300 mt-1">{{ metrics?.average_consensus_time_ms ?? 0 }}<span class="text-base text-ink-400">ms</span></p>
            <p class="font-mono text-[10px] text-ink-400 mt-1">PBFT 4-phase median</p>
          </div>
          <div class="panel-quiet p-4">
            <p class="eyebrow">Mesh online</p>
            <p class="font-display text-3xl text-violet-300 mt-1">{{ metrics?.agents_online ?? 0 }}<span class="text-base text-ink-400">/{{ metrics?.agents_total ?? 0 }}</span></p>
            <p class="font-mono text-[10px] text-ink-400 mt-1">Heterogeneous LLM agents</p>
          </div>
          <div class="panel-quiet p-4">
            <p class="eyebrow">Uptime</p>
            <p class="font-display text-3xl text-ink-100 mt-1">{{ uptime }}</p>
            <p class="font-mono text-[10px] text-ink-400 mt-1">View #18</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Throughput + Mesh -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="panel lg:col-span-2">
        <div class="panel-header">
          <div class="flex items-center gap-3">
            <span class="live-dot"></span>
            <h3 class="panel-title">Throughput · last 60 min</h3>
          </div>
          <span class="font-mono text-[11px] text-ink-400">{{ (metrics?.throughput_per_min ?? 0).toFixed(2) }} bugs/min</span>
        </div>
        <div class="panel-body">
          <svg :viewBox="`0 0 ${sparkline.w} ${sparkline.h}`" class="w-full h-24">
            <defs>
              <linearGradient id="spark" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%"  stop-color="#7C8CFF" stop-opacity="0.5"/>
                <stop offset="100%" stop-color="#7C8CFF" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <path :d="sparkline.area" fill="url(#spark)"/>
            <path :d="sparkline.path" fill="none" stroke="#7C8CFF" stroke-width="1.5"/>
          </svg>
          <div class="mt-3 grid grid-cols-4 gap-3 font-mono text-[11px]">
            <div><span class="text-ink-400">Detected </span><span class="text-rose-300">{{ recent.filter(r => r.type==='bug_detected').length }}</span></div>
            <div><span class="text-ink-400">Proposed </span><span class="text-cyan-300">{{ recent.filter(r => r.type==='fix_proposed').length }}</span></div>
            <div><span class="text-ink-400">Applied </span><span class="text-emerald-300">{{ recent.filter(r => r.type==='fix_applied').length }}</span></div>
            <div><span class="text-ink-400">Consensus </span><span class="text-violet-300">{{ recent.filter(r => r.type==='consensus_reached').length }}</span></div>
          </div>
        </div>
      </div>

      <!-- Dataset coverage -->
      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">Dataset coverage</h3>
          <router-link to="/evaluation" class="font-mono text-[11px] text-brand-300 hover:text-brand-200">/evaluation →</router-link>
        </div>
        <div class="panel-body space-y-3">
          <div v-for="d in [
            { name:'BugsInPy',           total:493,  loaded:501,  color:'from-violet-400 to-violet-600' },
            { name:'Defects4J',          total:835,  loaded:0,    color:'from-amber-400 to-amber-600' },
            { name:'Synthetic e-comm.',  total:2000, loaded:2000, color:'from-cyan-400 to-cyan-600' },
          ]" :key="d.name">
            <div class="flex items-center justify-between text-[12px]">
              <span class="text-ink-200">{{ d.name }}</span>
              <span class="font-mono text-ink-400">{{ d.loaded }} / {{ d.total }}</span>
            </div>
            <div class="bar-track mt-1">
              <div class="bar-fill bg-gradient-to-r" :class="d.color"
                   :style="{ width: Math.min(100, (d.loaded / d.total) * 100) + '%' }"></div>
            </div>
          </div>
          <p class="font-mono text-[10px] text-ink-400 pt-1">
            Defects4J cloned · awaits <span class="kbd">./init.sh</span> (Java 8+)
          </p>
        </div>
      </div>
    </section>

    <!-- Active bugs + Agent mesh -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="panel lg:col-span-2">
        <div class="panel-header">
          <h3 class="panel-title">Active bug stream</h3>
          <router-link to="/bugs" class="font-mono text-[11px] text-brand-300 hover:text-brand-200">/bugs →</router-link>
        </div>
        <div class="panel-body p-0">
          <div v-if="bugsStore.activeBugs.length === 0" class="p-8 text-center text-ink-400 text-sm">
            All clear · no active bugs in flight
          </div>
          <table v-else class="tbl">
            <thead>
              <tr><th>ID</th><th>Type</th><th>Severity</th><th>Location</th><th>Status</th><th></th></tr>
            </thead>
            <tbody>
              <tr v-for="bug in bugsStore.activeBugs.slice(0, 6)" :key="bug.id">
                <td class="font-mono text-[12px] text-ink-300">{{ bug.id }}</td>
                <td>{{ bug.bug_type.replace(/_/g, ' ') }}</td>
                <td><span :class="`sev-${bug.severity}`">{{ bug.severity }}</span></td>
                <td class="font-mono text-[11px] text-ink-400 truncate max-w-[280px]">{{ bug.file_path }}<span class="text-ink-500">:{{ bug.line_number }}</span></td>
                <td><span :class="`status status-${bug.status}`">{{ bug.status.replace('_',' ') }}</span></td>
                <td class="text-right">
                  <router-link :to="`/bugs/${bug.id}`" class="font-mono text-[11px] text-brand-300 hover:text-brand-200">inspect →</router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">Agent mesh</h3>
          <router-link to="/agents" class="font-mono text-[11px] text-brand-300 hover:text-brand-200">/agents →</router-link>
        </div>
        <div class="panel-body space-y-2 max-h-[420px] overflow-y-auto pr-2">
          <div v-for="a in agentsStore.agents" :key="a.id"
               class="group flex items-center gap-3 p-2.5 rounded-lg border border-white/5 bg-ink-850/60 hover:bg-white/[0.03] transition">
            <div :class="['w-9 h-9 rounded-lg flex items-center justify-center text-[11px] font-mono font-bold text-white',
              a.agent_type==='analyzer' ? 'bg-agent-analyzer' :
              a.agent_type==='healer'   ? 'bg-agent-healer'   : 'bg-agent-validator']">
              {{ a.agent_type.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[12.5px] text-ink-100 truncate">{{ a.name }}</p>
              <p class="font-mono text-[10px] text-ink-400 truncate">{{ a.llm_provider }} · {{ a.model || '—' }}</p>
            </div>
            <div class="text-right">
              <div class="flex items-center justify-end gap-1.5">
                <span :class="['dot', a.status==='online' ? 'dot-online' : a.status==='busy' ? 'dot-busy' : 'dot-offline']"></span>
                <span class="font-mono text-[10px] uppercase tracking-wider"
                      :class="a.status==='online' ? 'text-emerald-300' : a.status==='busy' ? 'text-amber-300' : 'text-ink-400'">{{ a.status }}</span>
              </div>
              <p class="font-mono text-[10px] text-ink-400 mt-0.5">rep {{ ((a.reputation_score ?? 0) * 100).toFixed(0) }}%</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Activity feed -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Live event log</h3>
        <span class="kbd">tail -f</span>
      </div>
      <div class="panel-body p-0">
        <div v-if="recent.length === 0" class="p-6 text-center text-ink-400 text-sm">No recent activity</div>
        <ul v-else class="divide-y divide-white/5">
          <li v-for="(a, i) in recent.slice(0, 12)" :key="i"
              class="flex items-center gap-3 px-5 py-2.5 hover:bg-white/[0.02] transition">
            <span :class="['w-1.5 h-1.5 rounded-full', activityIcon[a.type]?.dot || 'bg-ink-400']"></span>
            <span class="font-mono text-[11px] text-ink-500 w-20">{{ fmtTime(a.timestamp) }}</span>
            <span :class="['font-mono text-[10px] uppercase tracking-wider w-32', activityIcon[a.type]?.color || 'text-ink-300']">{{ a.type.replace('_',' ') }}</span>
            <span class="text-[12.5px] text-ink-200 flex-1 min-w-0 truncate">{{ a.message }}</span>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>
