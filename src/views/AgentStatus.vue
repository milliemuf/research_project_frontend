<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAgentsStore } from '@/stores/agents'

const agentsStore = useAgentsStore()
const filter = ref('all')

onMounted(() => {
  agentsStore.fetchAgents()
  agentsStore.fetchConsensusStatus()
})

const typeMeta = {
  analyzer:  { gradient: 'bg-agent-analyzer',  text: 'text-violet-300',  ring: 'ring-analyzer',  glow: 'shadow-glow-analyzer'  },
  healer:    { gradient: 'bg-agent-healer',    text: 'text-cyan-300',    ring: 'ring-healer',    glow: 'shadow-glow-healer'    },
  validator: { gradient: 'bg-agent-validator', text: 'text-emerald-300', ring: 'ring-validator', glow: 'shadow-glow-validator' },
}

const filtered = computed(() =>
  filter.value === 'all' ? agentsStore.agents : agentsStore.agents.filter(a => a.agent_type === filter.value)
)

const stats = computed(() => {
  // The BFT cluster is the voting validators (genuine 3f+1); the analyzer and
  // healer propose/feed but do not vote, so they are not counted in n.
  const n = agentsStore.agents.filter(a => a.agent_type === 'validator').length || 4
  const f = Math.floor((n - 1) / 3)
  return { n, f, quorum: 2 * f + 1, min: 3 * f + 1 }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="panel p-5 flex flex-wrap items-center justify-between gap-4">
      <div>
        <p class="eyebrow">Heterogeneous LLM agents under PBFT</p>
        <h2 class="font-display text-xl text-ink-100">Agent Mesh</h2>
      </div>
      <div class="flex items-center gap-1 p-1 rounded-lg bg-ink-850/60 border border-white/5">
        <button v-for="t in ['all', 'analyzer', 'healer', 'validator']" :key="t"
          @click="filter = t"
          :class="['px-3 py-1.5 rounded-md font-mono text-[11px] uppercase tracking-wider transition',
            filter === t ? 'bg-white/10 text-ink-100' : 'text-ink-400 hover:text-ink-200']">
          {{ t }}
        </button>
      </div>
    </section>

    <!-- Mesh stats -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Byzantine consensus configuration</h3>
        <span class="font-mono text-[11px]" :class="agentsStore.isConsensusReady ? 'text-emerald-300' : 'text-rose-300'">
          {{ agentsStore.isConsensusReady ? '● quorum reached' : '● awaiting quorum' }}
        </span>
      </div>
      <div class="panel-body grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="panel-quiet p-4">
          <p class="eyebrow">Cluster size · N</p>
          <p class="font-display text-3xl text-ink-100 mt-1">{{ stats.n }}</p>
          <p class="font-mono text-[10px] text-ink-400 mt-1">Independent validators</p>
        </div>
        <div class="panel-quiet p-4">
          <p class="eyebrow">Fault tolerance · f</p>
          <p class="font-display text-3xl text-amber-300 mt-1">{{ stats.f }}</p>
          <p class="font-mono text-[10px] text-ink-400 mt-1">Byzantine nodes survivable</p>
        </div>
        <div class="panel-quiet p-4">
          <p class="eyebrow">Quorum · 2f+1</p>
          <p class="font-display text-3xl text-emerald-300 mt-1">{{ stats.quorum }}</p>
          <p class="font-mono text-[10px] text-ink-400 mt-1">Required matching votes</p>
        </div>
        <div class="panel-quiet p-4">
          <p class="eyebrow">Min cluster · 3f+1</p>
          <p class="font-display text-3xl text-cyan-300 mt-1">{{ stats.min }}</p>
          <p class="font-mono text-[10px] text-ink-400 mt-1">Liveness lower bound</p>
        </div>
      </div>
    </section>

    <!-- Agent grid -->
    <section class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <div v-for="a in filtered" :key="a.id"
        :class="['panel overflow-hidden transition-transform hover:-translate-y-0.5',
          a.status === 'online' ? typeMeta[a.agent_type].glow : '']">
        <div :class="['h-1', typeMeta[a.agent_type].gradient]"></div>
        <div class="p-5">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div :class="['w-11 h-11 rounded-xl flex items-center justify-center text-white font-mono text-base font-bold',
                typeMeta[a.agent_type].gradient]">
                {{ a.agent_type.charAt(0).toUpperCase() }}
              </div>
              <div>
                <p class="font-medium text-ink-100 leading-tight">{{ a.name.split(' - ')[0].trim() }}</p>
                <p :class="['font-mono text-[11px] mt-0.5', typeMeta[a.agent_type].text]">{{ a.agent_type }}</p>
              </div>
            </div>
            <div class="flex items-center gap-1.5">
              <span :class="['dot', a.status === 'online' ? 'dot-online' : a.status === 'busy' ? 'dot-busy' : 'dot-offline']"></span>
              <span class="font-mono text-[10px] uppercase tracking-wider"
                :class="a.status === 'online' ? 'text-emerald-300' : a.status === 'busy' ? 'text-amber-300' : 'text-ink-400'">
                {{ a.status }}
              </span>
            </div>
          </div>

          <div class="mt-4 grid grid-cols-2 gap-3 text-[12px]">
            <div>
              <p class="eyebrow">Provider</p>
              <p class="font-mono text-ink-200 mt-0.5">{{ a.llm_provider }}</p>
            </div>
            <div>
              <p class="eyebrow">Model</p>
              <p class="font-mono text-ink-200 mt-0.5 truncate">{{ a.model || a.name.split(' - ')[1]?.trim() || '—' }}</p>
            </div>
            <div>
              <p class="eyebrow">{{ a.agent_type === 'validator' ? 'Accept rate' : 'Tasks' }}</p>
              <p class="font-mono text-ink-200 mt-0.5">{{ a.accepted_proposals ?? a.successful_tasks ?? 0 }}/{{ a.total_proposals ?? a.total_tasks ?? 0 }}</p>
            </div>
            <div>
              <p class="eyebrow">Avg latency</p>
              <p class="font-mono text-ink-200 mt-0.5">{{ a.avg_latency_ms ?? a.average_latency_ms ?? 0 }}ms</p>
            </div>
          </div>

          <div class="mt-4">
            <div class="flex items-center justify-between text-[11px]">
              <span class="eyebrow">Reputation</span>
              <span class="font-mono" :class="typeMeta[a.agent_type].text">{{ ((a.reputation_score ?? 0) * 100).toFixed(1) }}%</span>
            </div>
            <div class="bar-track mt-1.5">
              <div :class="['bar-fill', typeMeta[a.agent_type].gradient]"
                   :style="{ width: ((a.reputation_score ?? 0) * 100) + '%' }"></div>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between">
            <div class="flex items-center gap-2 text-[11px] font-mono text-ink-400">
              <span>uptime</span>
              <span class="text-ink-200">{{ (a.uptime_pct ?? 99).toFixed(1) }}%</span>
            </div>
            <button class="btn btn-ghost text-[10px]" :disabled="a.status === 'online'">
              {{ a.status === 'online' ? 'Healthy' : 'Restart' }}
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
