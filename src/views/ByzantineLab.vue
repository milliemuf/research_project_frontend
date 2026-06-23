<script setup>
import { onMounted } from 'vue'
import { useByzantineLabStore } from '@/stores/byzantineLab'

const lab = useByzantineLabStore()

onMounted(() => lab.fetchHistory())

const FAULT_TYPES = [
  { key: 'bad_proposal', label: 'Bad Proposal', tip: 'Agent submits an incorrect fix' },
  { key: 'drop_message', label: 'Drop Msg', tip: 'Agent silently drops consensus messages' },
  { key: 'equivocate',   label: 'Equivocate', tip: 'Agent sends conflicting votes' },
]

function agentBg(type) {
  return type === 'analyzer' ? 'bg-agent-analyzer'
       : type === 'healer'   ? 'bg-agent-healer'
       :                       'bg-agent-validator'
}
function agentRing(type) {
  return type === 'analyzer' ? 'ring-analyzer'
       : type === 'healer'   ? 'ring-healer'
       :                       'ring-validator'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header + summary -->
    <section class="panel px-5 py-3 flex flex-wrap items-start gap-6 justify-between">
      <div class="max-w-xl">
        <p class="eyebrow">Fault tolerance testing</p>
        <h2 class="font-display text-lg text-ink-100">Byzantine Injection Lab</h2>
        <p class="text-[12px] text-ink-400 mt-1 leading-relaxed">
          Inject faults into individual agents and run PBFT scenarios. The system tolerates up to
          <span class="text-ink-100 font-mono">f = {{ Math.floor(((lab.agents.length || 4) - 1) / 3) }}</span> faulty validators
          out of <span class="text-ink-100 font-mono">{{ lab.agents.length || 4 }}</span> total (3f+1 requirement).
        </p>
      </div>
      <div class="grid grid-cols-4 gap-2">
        <div class="panel-quiet p-2.5 text-center">
          <p class="eyebrow">Runs</p>
          <p class="font-display text-xl text-ink-100 mt-0.5">{{ lab.summary.total_runs }}</p>
        </div>
        <div class="panel-quiet p-2.5 text-center">
          <p class="eyebrow">Survived</p>
          <p class="font-display text-xl text-emerald-300 mt-0.5">{{ lab.summary.survived }}</p>
        </div>
        <div class="panel-quiet p-2.5 text-center">
          <p class="eyebrow">Failed</p>
          <p class="font-display text-xl text-rose-300 mt-0.5">{{ lab.summary.failed }}</p>
        </div>
        <div class="panel-quiet p-2.5 text-center">
          <p class="eyebrow">Rate</p>
          <p class="font-display text-xl text-brand-300 mt-0.5">{{ (lab.summary.survival_rate * 100).toFixed(1) }}%</p>
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 xl:grid-cols-12 gap-4">
      <!-- Agent controls -->
      <div class="panel xl:col-span-7">
        <div class="panel-header">
          <h3 class="panel-title">Fault injection controls</h3>
          <button class="btn btn-danger" @click="lab.runScenario()" :disabled="lab.running">
            <svg v-if="lab.running" class="w-3 h-3 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="31.4" stroke-dashoffset="10"/></svg>
            {{ lab.running ? 'Running...' : 'Run Scenario' }}
          </button>
        </div>
        <div class="panel-body grid grid-cols-1 md:grid-cols-3 gap-3">
          <div v-for="agent in lab.agents" :key="agent.id"
            class="panel-quiet p-3 space-y-2"
            :class="[agentRing(agent.agent_type), agent.fault_injected ? 'ring-rose-500/40' : '']">
            <div class="flex items-center gap-2">
              <div :class="['w-7 h-7 rounded-md flex items-center justify-center text-[10px] font-mono font-bold text-white', agentBg(agent.agent_type)]">
                {{ agent.agent_type.charAt(0).toUpperCase() }}
              </div>
              <div class="min-w-0">
                <p class="text-[11.5px] text-ink-100 truncate">{{ agent.name }}</p>
                <p class="font-mono text-[9px] text-ink-400">{{ agent.llm_provider }}</p>
              </div>
            </div>
            <div class="flex gap-1 flex-wrap">
              <button v-for="ft in FAULT_TYPES" :key="ft.key"
                :title="ft.tip"
                @click="lab.toggleFault(agent.id, ft.key)"
                :class="['text-[9px] px-1.5 py-1 rounded-md font-mono uppercase tracking-wider transition',
                  agent.fault_injected && agent.fault_type === ft.key
                    ? 'bg-rose-500/20 text-rose-300 ring-1 ring-rose-500/40'
                    : 'bg-white/5 text-ink-400 ring-1 ring-white/10 hover:bg-white/10']">
                {{ ft.label }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Results feed -->
      <div class="panel xl:col-span-5">
        <div class="panel-header">
          <h3 class="panel-title">Scenario results</h3>
          <span class="font-mono text-[10px] text-ink-400">{{ lab.results.length }} runs</span>
        </div>
        <div class="panel-body p-0">
          <div v-if="!lab.results.length" class="p-6 text-center text-ink-400 text-[12px]">No scenarios run yet — inject faults and click Run</div>
          <ul v-else class="divide-y divide-white/5 max-h-[500px] overflow-y-auto">
            <li v-for="r in lab.results" :key="r.id" class="p-3 hover:bg-white/[0.02] transition space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="font-mono text-[11px] text-ink-300">{{ r.id }}</span>
                <span :class="r.survived ? 'status status-resolved' : 'status status-failed'">
                  {{ r.survived ? 'survived' : 'failed' }}
                </span>
              </div>
              <div class="flex flex-wrap gap-1">
                <span v-for="(f, i) in r.faults" :key="i"
                  class="tag tag-rose text-[8px]">{{ f.fault_type.replace(/_/g,' ') }}</span>
                <span v-if="!r.faults.length" class="tag tag-slate text-[8px]">no faults</span>
              </div>
              <div class="flex items-center gap-3 font-mono text-[10px] text-ink-400">
                <span v-if="r.survived">Recovery: {{ r.rounds_to_recover }} rnd</span>
                <span>{{ r.duration_ms }}ms</span>
              </div>
              <details class="mt-1">
                <summary class="font-mono text-[10px] text-ink-500 cursor-pointer hover:text-ink-300">log</summary>
                <ul class="mt-1 space-y-0.5">
                  <li v-for="(line, li) in r.log" :key="li" class="font-mono text-[10px] text-ink-400 pl-2 border-l border-white/5">{{ line }}</li>
                </ul>
              </details>
            </li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>
