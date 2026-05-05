<script setup>
import { ref, onMounted, computed } from 'vue'
import { useBugsStore } from '@/stores/bugs'

const bugsStore = useBugsStore()
const filterStatus = ref('')
const filterSeverity = ref('')
const search = ref('')

onMounted(() => bugsStore.fetchBugs())

const filtered = computed(() => {
  let bugs = bugsStore.bugs
  if (filterStatus.value)   bugs = bugs.filter(b => b.status === filterStatus.value)
  if (filterSeverity.value) bugs = bugs.filter(b => b.severity === filterSeverity.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    bugs = bugs.filter(b =>
      b.id.toLowerCase().includes(q) ||
      b.bug_type.toLowerCase().includes(q) ||
      (b.file_path || '').toLowerCase().includes(q) ||
      (b.project || '').toLowerCase().includes(q)
    )
  }
  return bugs
})

const fmt = (ts) => new Date(ts).toLocaleString([], {
  month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit'
})

const counts = computed(() => {
  const by = (k) => bugsStore.bugs.reduce((acc, b) => (acc[b[k]] = (acc[b[k]] || 0) + 1, acc), {})
  return { byStatus: by('status'), bySeverity: by('severity') }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="panel p-5 flex flex-wrap items-center gap-4 justify-between">
      <div>
        <p class="eyebrow">Detected · proposed · validated</p>
        <h2 class="font-display text-xl text-ink-100">Bug Stream</h2>
      </div>
      <div class="flex flex-wrap items-center gap-2 font-mono text-[11px]">
        <span class="tag tag-rose">CRIT {{ counts.bySeverity.critical || 0 }}</span>
        <span class="tag tag-amber">HIGH {{ counts.bySeverity.high || 0 }}</span>
        <span class="tag tag-slate">MED {{ counts.bySeverity.medium || 0 }}</span>
        <span class="tag tag-emerald">LOW {{ counts.bySeverity.low || 0 }}</span>
        <span class="kbd">Σ {{ bugsStore.bugs.length }}</span>
      </div>
    </section>

    <!-- Filters -->
    <section class="panel p-4 flex flex-wrap items-center gap-3">
      <div class="flex-1 min-w-[260px] relative">
        <input v-model="search" placeholder="Search bug id, type, file, project…"
               class="w-full bg-ink-850/70 border border-white/10 rounded-lg px-3 py-2 text-sm font-mono text-ink-100 placeholder-ink-500 focus:outline-none focus:border-brand-500/60 focus:ring-2 focus:ring-brand-500/20" />
      </div>
      <select v-model="filterStatus"
        class="bg-ink-850/70 border border-white/10 rounded-lg px-3 py-2 text-sm font-mono text-ink-100 focus:outline-none focus:border-brand-500/60">
        <option value="">all statuses</option>
        <option value="detected">detected</option>
        <option value="analyzing">analyzing</option>
        <option value="fix_proposed">fix proposed</option>
        <option value="consensus_pending">consensus pending</option>
        <option value="resolved">resolved</option>
        <option value="failed">failed</option>
      </select>
      <select v-model="filterSeverity"
        class="bg-ink-850/70 border border-white/10 rounded-lg px-3 py-2 text-sm font-mono text-ink-100 focus:outline-none focus:border-brand-500/60">
        <option value="">all severities</option>
        <option value="critical">critical</option>
        <option value="high">high</option>
        <option value="medium">medium</option>
        <option value="low">low</option>
      </select>
      <span class="font-mono text-[11px] text-ink-400">{{ filtered.length }} match</span>
    </section>

    <!-- Table -->
    <section class="panel">
      <div class="panel-body p-0">
        <table class="tbl">
          <thead>
            <tr><th>ID</th><th>Type</th><th>Severity</th><th>Project</th><th>Location</th><th>Status</th><th>Detected</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="b in filtered" :key="b.id">
              <td class="font-mono text-[12px] text-ink-300">{{ b.id }}</td>
              <td class="text-ink-100">{{ b.bug_type.replace(/_/g, ' ') }}</td>
              <td><span :class="`sev-${b.severity}`">{{ b.severity }}</span></td>
              <td class="font-mono text-[11px] text-ink-300">{{ b.project }}</td>
              <td class="font-mono text-[11px] text-ink-400 truncate max-w-[300px]">
                {{ b.file_path }}<span class="text-ink-500">:{{ b.line_number }}</span>
              </td>
              <td><span :class="`status status-${b.status}`">{{ b.status.replace('_',' ') }}</span></td>
              <td class="font-mono text-[11px] text-ink-400">{{ fmt(b.detected_at) }}</td>
              <td class="text-right">
                <router-link :to="`/bugs/${b.id}`" class="font-mono text-[11px] text-brand-300 hover:text-brand-200">inspect →</router-link>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="filtered.length === 0" class="p-10 text-center text-ink-400 text-sm">
          No bugs match these filters
        </div>
      </div>
    </section>
  </div>
</template>
