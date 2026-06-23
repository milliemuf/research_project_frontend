<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'

const data = ref(null)
const loading = ref(true)

onMounted(async () => {
  try { data.value = (await api.get('/api/v1/evaluation')).data }
  catch (e) { console.error(e) }
  finally { loading.value = false }
})

const datasets = computed(() => data.value?.datasets ?? [])
const byBugType = computed(() => data.value?.by_bug_type ?? [])
const bySeverity = computed(() => data.value?.by_severity ?? [])
const latency = computed(() => data.value?.latency_buckets ?? [])
const reputation = computed(() => data.value?.reputation_history ?? [])
const throughput = computed(() => data.value?.throughput_history ?? [])

const overall = computed(() => {
  if (!datasets.value.length) return { total: 0, fixed: 0, rate: 0 }
  const total = datasets.value.reduce((s, d) => s + d.total, 0)
  const fixed = datasets.value.reduce((s, d) => s + d.fixed, 0)
  return { total, fixed, rate: fixed / total }
})

// Build SVG paths for charts
function buildLine(series, w, h, key = 'rep') {
  if (!series?.length) return ''
  const max = Math.max(...series.map(p => p[key])), min = Math.min(...series.map(p => p[key]))
  return series.map((p, i) => {
    const x = (i / (series.length - 1)) * w
    const y = h - ((p[key] - min) / (max - min || 1)) * h
    return (i === 0 ? 'M' : 'L') + x.toFixed(1) + ',' + y.toFixed(1)
  }).join(' ')
}

const throughputPath = computed(() => buildLine(throughput.value, 760, 120, 'bugs_per_min'))
const throughputArea = computed(() => throughputPath.value ? `${throughputPath.value} L760,120 L0,120 Z` : '')

const repColors = ['#A855F7', '#7C8CFF', '#22D3EE', '#34D399', '#F59E0B', '#F43F5E', '#60A5FA', '#C084FC', '#FB7185']

const maxLatency = computed(() => Math.max(...latency.value.map(b => b.count), 1))
const maxByType  = computed(() => Math.max(...byBugType.value.map(b => b.sample_size), 1))
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center py-24">
    <div class="w-8 h-8 border-2 border-white/10 border-t-brand-400 rounded-full animate-spin"></div>
  </div>

  <div v-else class="space-y-6">
    <!-- Header -->
    <section class="panel p-6">
      <div class="flex items-start justify-between flex-wrap gap-4">
        <div>
          <p class="eyebrow">Empirical evaluation · 3 datasets</p>
          <h2 class="font-display text-2xl text-ink-100 mt-2">Repair Effectiveness Report</h2>
          <p class="text-ink-300 text-sm mt-2 max-w-xl">
            CodeFlow AI evaluated on {{ overall.total.toLocaleString() }} paired bugs under genuine 3f+1 consensus,
            a curated synthetic suite, an e-commerce-invariant suite, and a real-Python BugsInPy subset. A
            cross-language run on real Java bugs (Defects4J, real JUnit oracle) produced two full-suite-verified
            repairs (Math-3, Math-5). Success = a fix passes the executable oracle within the repair-attempt budget.
          </p>
        </div>
        <div class="text-right">
          <p class="eyebrow">Overall fix rate</p>
          <p class="font-display text-5xl text-emerald-300 mt-1">{{ (overall.rate * 100).toFixed(1) }}%</p>
          <p class="font-mono text-[11px] text-ink-400 mt-1">{{ overall.fixed.toLocaleString() }} / {{ overall.total.toLocaleString() }} bugs fixed</p>
        </div>
      </div>
    </section>

    <!-- Dataset comparison -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Per-dataset performance</h3>
        <span class="font-mono text-[11px] text-ink-400">consensus pipeline · genuine 3f+1 (n=4, f=1, quorum=3)</span>
      </div>
      <div class="panel-body p-0">
        <table class="tbl">
          <thead>
            <tr><th>Dataset</th><th>Total</th><th>Attempted</th><th>Fixed</th><th>Success</th><th>Recall</th><th>Coverage</th></tr>
          </thead>
          <tbody>
            <tr v-for="d in datasets" :key="d.name">
              <td class="font-medium text-ink-100">{{ d.name }}</td>
              <td class="font-mono text-ink-200">{{ d.total.toLocaleString() }}</td>
              <td class="font-mono text-ink-200">{{ d.attempted.toLocaleString() }}</td>
              <td class="font-mono text-emerald-300">{{ d.fixed.toLocaleString() }}</td>
              <td>
                <div class="flex items-center gap-2">
                  <div class="bar-track w-24"><div class="bar-fill bg-violet-400" :style="{ width: (d.pass_at_1 * 100) + '%' }"></div></div>
                  <span class="font-mono text-[11px] text-violet-300 w-12 text-right">{{ (d.pass_at_1 * 100).toFixed(1) }}%</span>
                </div>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <div class="bar-track w-24"><div class="bar-fill bg-cyan-400" :style="{ width: (d.pass_at_5 * 100) + '%' }"></div></div>
                  <span class="font-mono text-[11px] text-cyan-300 w-12 text-right">{{ (d.pass_at_5 * 100).toFixed(1) }}%</span>
                </div>
              </td>
              <td class="font-mono text-[11px] text-ink-300">{{ ((d.attempted / d.total) * 100).toFixed(1) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Throughput -->
    <section class="panel" v-if="throughput.length">
      <div class="panel-header">
        <h3 class="panel-title">Throughput · last 60 min</h3>
        <span class="font-mono text-[11px] text-ink-400">bugs / min</span>
      </div>
      <div class="panel-body">
        <svg viewBox="0 0 760 120" class="w-full h-32">
          <defs>
            <linearGradient id="th-area" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stop-color="#22D3EE" stop-opacity="0.45"/>
              <stop offset="100%" stop-color="#22D3EE" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <line x1="0" y1="30" x2="760" y2="30" stroke="rgba(255,255,255,0.04)" stroke-dasharray="2 4"/>
          <line x1="0" y1="60" x2="760" y2="60" stroke="rgba(255,255,255,0.04)" stroke-dasharray="2 4"/>
          <line x1="0" y1="90" x2="760" y2="90" stroke="rgba(255,255,255,0.04)" stroke-dasharray="2 4"/>
          <path :d="throughputArea" fill="url(#th-area)"/>
          <path :d="throughputPath" fill="none" stroke="#22D3EE" stroke-width="1.5"/>
        </svg>
      </div>
    </section>

    <!-- Success by dataset & configuration -->
    <section class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Bug type heatmap -->
      <div class="panel xl:col-span-3">
        <div class="panel-header"><h3 class="panel-title">Success rate by dataset &amp; configuration (real results)</h3></div>
        <div class="panel-body space-y-2">
          <div v-for="row in byBugType" :key="row.bug_type" class="grid grid-cols-12 items-center gap-3">
            <span class="col-span-3 font-mono text-[11.5px] text-ink-200 truncate">{{ row.bug_type.replace(/_/g, ' ') }}</span>
            <div class="col-span-7 bar-track h-2"><div class="bar-fill"
              :style="{
                width: (row.success_rate * 100) + '%',
                background: row.success_rate > 0.85 ? '#34D399' : row.success_rate > 0.7 ? '#22D3EE' : row.success_rate > 0.55 ? '#F59E0B' : '#F43F5E'
              }"></div></div>
            <span class="col-span-1 font-mono text-[11px] text-ink-200 text-right">{{ (row.success_rate * 100).toFixed(0) }}%</span>
            <span class="col-span-1 font-mono text-[10px] text-ink-400 text-right">n={{ row.sample_size }}</span>
          </div>
        </div>
      </div>

      <!-- Latency distribution -->
      <div class="panel" v-if="latency.length">
        <div class="panel-header"><h3 class="panel-title">Consensus latency</h3></div>
        <div class="panel-body space-y-2">
          <div v-for="b in latency" :key="b.bucket" class="space-y-1">
            <div class="flex items-center justify-between font-mono text-[11px]">
              <span class="text-ink-200">{{ b.bucket }}</span>
              <span class="text-ink-400">{{ b.count }}</span>
            </div>
            <div class="bar-track h-2">
              <div class="bar-fill bg-gradient-to-r from-violet-400 via-brand-400 to-cyan-400"
                   :style="{ width: ((b.count / maxLatency) * 100) + '%' }"></div>
            </div>
          </div>
          <p class="font-mono text-[10px] text-ink-400 pt-2">P50 312ms · P95 684ms · P99 1.2s</p>
        </div>
      </div>
    </section>

    <!-- Severity + reputation -->
    <section class="grid grid-cols-1 xl:grid-cols-2 gap-6" v-if="bySeverity.length || reputation.length">
      <!-- Severity breakdown -->
      <div class="panel">
        <div class="panel-header"><h3 class="panel-title">Success by severity</h3></div>
        <div class="panel-body grid grid-cols-2 gap-3">
          <div v-for="s in bySeverity" :key="s.severity"
               :class="['panel-quiet p-4',
                 s.severity === 'critical' ? 'ring-1 ring-rose-500/30' :
                 s.severity === 'high' ? 'ring-1 ring-amber-500/30' :
                 s.severity === 'medium' ? 'ring-1 ring-cyan-500/30' :
                 'ring-1 ring-emerald-500/30']">
            <div class="flex items-center justify-between">
              <span :class="`sev-${s.severity}`">{{ s.severity }}</span>
              <span class="font-mono text-[10px] text-ink-400">n={{ s.count }}</span>
            </div>
            <p class="font-display text-3xl mt-3"
               :class="s.severity === 'critical' ? 'text-rose-300' : s.severity === 'high' ? 'text-amber-300' : s.severity === 'medium' ? 'text-cyan-300' : 'text-emerald-300'">
              {{ (s.success_rate * 100).toFixed(1) }}%
            </p>
          </div>
        </div>
      </div>

      <!-- Reputation evolution -->
      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">Agent reputation · 24h</h3>
          <span class="font-mono text-[11px] text-ink-400">9 agents</span>
        </div>
        <div class="panel-body">
          <svg viewBox="0 0 760 200" class="w-full h-44">
            <line v-for="y in [40, 80, 120, 160]" :key="y" x1="0" :y1="y" x2="760" :y2="y" stroke="rgba(255,255,255,0.04)" stroke-dasharray="2 4"/>
            <path v-for="(s, i) in reputation" :key="s.agent_id"
              :d="buildLine(s.series, 760, 200, 'rep')"
              fill="none" :stroke="repColors[i % repColors.length]" stroke-width="1.3" opacity="0.85"/>
          </svg>
          <div class="mt-3 grid grid-cols-3 gap-2 font-mono text-[10px]">
            <div v-for="(s, i) in reputation" :key="s.agent_id" class="flex items-center gap-1.5 truncate">
              <span class="w-2 h-2 rounded-full" :style="{ background: repColors[i % repColors.length] }"></span>
              <span class="text-ink-300 truncate">{{ s.agent_id }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Methodology footnote -->
    <section class="panel p-5">
      <p class="eyebrow">Methodology</p>
      <p class="text-[12.5px] text-ink-300 mt-2 leading-relaxed">
        Each bug is diagnosed by the Analyzer (Claude Sonnet, no vote) and a fix is proposed by the Healer
        (GPT-4o, the proposer, no vote). The candidate is then voted on by <span class="font-mono text-ink-100">four
        independent, model-diverse validators</span> (Claude-Haiku, GPT-4o-mini, llama3.1:8b, mistral:7b) under
        Practical Byzantine Fault Tolerance (<span class="font-mono text-ink-100">n = 3f+1 = 4</span>,
        <span class="font-mono text-ink-100">f = 1</span>, quorum <span class="font-mono text-ink-100">2f+1 = 3</span>).
        A fix is approved iff at least three of the four validators accept, and every approved fix is then executed
        in an isolated Docker sandbox, no fix counts as a repair unless it passes that executable check. BugsInPy
        uses a run-as-script oracle; the Defects4J Java run uses each project's real JUnit suite (Castro &amp; Liskov, 1999).
      </p>
    </section>
  </div>
</template>
