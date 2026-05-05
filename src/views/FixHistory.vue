<script setup>
import { ref, onMounted, computed } from 'vue'
import { useBugsStore } from '@/stores/bugs'
import { mockAgents } from '@/services/mock'

const bugsStore = useBugsStore()
const filter = ref('all')

onMounted(() => bugsStore.fetchBugs())

// Build fix history from resolved/failed bugs
const history = computed(() => {
  const healers = mockAgents.filter(a => a.agent_type === 'healer')
  return bugsStore.bugs
    .filter(b => ['resolved', 'failed'].includes(b.status))
    .map((b, i) => ({
      id: `fix-${b.id}`,
      bug_id: b.id,
      bug_type: b.bug_type,
      agent: healers[i % healers.length],
      confidence: b.confidence ?? (0.65 + Math.random() * 0.3),
      status: b.status === 'resolved' ? 'applied' : 'rejected',
      created_at: b.detected_at,
      applied_at: b.status === 'resolved' ? new Date(new Date(b.detected_at).getTime() + 1000 * 60 * 5).toISOString() : null,
      duration_ms: 200 + Math.floor(Math.random() * 600),
      lines_changed: 1 + Math.floor(Math.random() * 12),
    }))
    .filter(f => filter.value === 'all' ? true : f.status === filter.value)
})

const fmt = (ts) => ts ? new Date(ts).toLocaleString([], { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—'
</script>

<template>
  <div class="space-y-6">
    <section class="panel p-5 flex flex-wrap items-center justify-between gap-4">
      <div>
        <p class="eyebrow">Validated &amp; merged via PBFT consensus</p>
        <h2 class="font-display text-xl text-ink-100">Fix History</h2>
      </div>
      <div class="flex items-center gap-1 p-1 rounded-lg bg-ink-850/60 border border-white/5">
        <button v-for="t in ['all', 'applied', 'rejected']" :key="t"
          @click="filter = t"
          :class="['px-3 py-1.5 rounded-md font-mono text-[11px] uppercase tracking-wider transition',
            filter === t ? 'bg-white/10 text-ink-100' : 'text-ink-400 hover:text-ink-200']">
          {{ t }}
        </button>
      </div>
    </section>

    <section class="panel">
      <div class="panel-body p-0">
        <table class="tbl">
          <thead>
            <tr><th>Fix</th><th>Bug</th><th>Healer</th><th>Confidence</th><th>Δ Lines</th><th>Latency</th><th>Result</th><th>Applied</th></tr>
          </thead>
          <tbody>
            <tr v-for="f in history" :key="f.id">
              <td class="font-mono text-[11px] text-ink-400">{{ f.id }}</td>
              <td>
                <router-link :to="`/bugs/${f.bug_id}`" class="font-mono text-[12px] text-brand-300 hover:text-brand-200">{{ f.bug_id }}</router-link>
                <p class="font-mono text-[10px] text-ink-500 mt-0.5">{{ f.bug_type.replace(/_/g, ' ') }}</p>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 rounded-md bg-agent-healer flex items-center justify-center text-white font-mono text-[10px] font-bold">H</div>
                  <span class="font-mono text-[11px] text-cyan-300">{{ f.agent.llm_provider }}</span>
                </div>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <div class="bar-track w-20"><div class="bar-fill bg-cyan-400" :style="{ width: (f.confidence * 100) + '%' }"></div></div>
                  <span class="font-mono text-[11px] text-ink-200 w-9">{{ (f.confidence * 100).toFixed(0) }}%</span>
                </div>
              </td>
              <td class="font-mono text-[12px] text-ink-200">+{{ f.lines_changed }}</td>
              <td class="font-mono text-[12px] text-ink-200">{{ f.duration_ms }}ms</td>
              <td><span :class="['status', f.status === 'applied' ? 'status-resolved' : 'status-failed']">{{ f.status }}</span></td>
              <td class="font-mono text-[11px] text-ink-400">{{ fmt(f.applied_at) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="history.length === 0" class="p-10 text-center text-ink-400 text-sm">No fixes recorded</div>
      </div>
    </section>
  </div>
</template>
