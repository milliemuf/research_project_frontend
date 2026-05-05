<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useBugsStore } from '@/stores/bugs'
import { mockAgents } from '@/services/mock'

const route = useRoute()
const bugsStore = useBugsStore()
const loading = ref(true)
const selectedAgent = ref(null)

onMounted(async () => {
  try {
    await bugsStore.fetchBugs()
    const id = route.params.id
    const found = bugsStore.bugs.find(b => b.id === id)
    if (found) bugsStore.currentBug = found
  } finally {
    loading.value = false
  }
})

const bug = computed(() => bugsStore.currentBug || bugsStore.bugs[0])

// Synthesize agent proposals around the chosen fix so the debate view is rich
const proposals = computed(() => {
  if (!bug.value) return []
  const healers = mockAgents.filter(a => a.agent_type === 'healer')
  const variants = [
    {
      label: 'Type-safe Decimal coercion',
      reasoning: 'Detected float-precision risk in financial path. Coerce inputs to Decimal at boundary, quantize on output to currency precision. Avoids cumulative rounding error across cart line items.',
      confidence: 0.93,
      vote: 'prepare+commit',
      result: 'accepted',
      code: bug.value.proposed_fix,
    },
    {
      label: 'Try/except + log + retry',
      reasoning: 'Less invasive — wrap the offending expression and surface to monitoring. Keeps existing call shape but masks underlying numeric bug; validators flagged this as treating symptom rather than cause.',
      confidence: 0.71,
      vote: 'prepare',
      result: 'rejected',
      code: `try:\n    ${bug.value.original_code.replace(/\n/g, '\n    ')}\nexcept (ValueError, TypeError) as e:\n    logger.exception('numeric path failed: %s', e)\n    raise PaymentError(str(e)) from e`,
    },
    {
      label: 'Schema-level guard via Pydantic',
      reasoning: 'Move responsibility upstream: enforce types at the request model (Pydantic v2) before the handler executes. Validators noted this is correct but out-of-scope for the bug locus.',
      confidence: 0.82,
      vote: 'prepare',
      result: 'rejected',
      code: `class PriceRequest(BaseModel):\n    price: Decimal = Field(..., ge=0, decimal_places=2)\n    quantity: int   = Field(..., ge=1, le=MAX_QTY)\n\n# handler now receives validated Decimal\n${bug.value.proposed_fix}`,
    },
  ]
  return healers.slice(0, 3).map((a, i) => ({ ...variants[i], agent: a }))
})

const acceptedProposal = computed(() => proposals.value.find(p => p.result === 'accepted'))
const activeProposal = computed(() => selectedAgent.value
  ? proposals.value.find(p => p.agent.id === selectedAgent.value)
  : acceptedProposal.value)

// Diff lines: split bug.original_code vs activeProposal.code
function diffLines(a, b) {
  const A = (a || '').split('\n')
  const B = (b || '').split('\n')
  const out = []
  out.push({ type: 'hunk', text: `@@ -1,${A.length} +1,${B.length} @@` })
  A.forEach(line => out.push({ type: 'del', text: line }))
  B.forEach(line => out.push({ type: 'add', text: line }))
  return out
}
const diff = computed(() => activeProposal.value ? diffLines(bug.value.original_code, activeProposal.value.code) : [])

const validators = computed(() => mockAgents.filter(a => a.agent_type === 'validator').slice(0, 3))
const analyzers  = computed(() => mockAgents.filter(a => a.agent_type === 'analyzer').slice(0, 3))
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center py-24">
    <div class="w-8 h-8 border-2 border-white/10 border-t-brand-400 rounded-full animate-spin"></div>
  </div>

  <div v-else-if="bug" class="space-y-6">
    <!-- Header card -->
    <section class="panel p-6">
      <div class="flex items-start justify-between gap-6 flex-wrap">
        <div class="flex-1 min-w-[280px]">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="kbd">{{ bug.id }}</span>
            <span :class="`sev-${bug.severity}`">{{ bug.severity }}</span>
            <span :class="`status status-${bug.status}`">{{ bug.status.replace('_',' ') }}</span>
          </div>
          <h2 class="font-display text-2xl text-ink-100 mt-3">{{ bug.bug_type.replace(/_/g, ' ') }}</h2>
          <p class="font-mono text-[12px] text-ink-400 mt-1">
            <span class="text-ink-200">{{ bug.project }}</span> · {{ bug.file_path }}<span class="text-ink-500">:{{ bug.line_number }}</span>
          </p>
        </div>
        <div class="grid grid-cols-3 gap-3 min-w-[300px]">
          <div class="panel-quiet p-3">
            <p class="eyebrow">Confidence</p>
            <p class="font-display text-xl text-cyan-300 mt-1">{{ ((bug.confidence ?? 0.85) * 100).toFixed(0) }}%</p>
          </div>
          <div class="panel-quiet p-3">
            <p class="eyebrow">Prepares</p>
            <p class="font-display text-xl text-violet-300 mt-1">{{ bug.consensus_votes?.prepare ?? 0 }}<span class="text-ink-500 text-sm">/9</span></p>
          </div>
          <div class="panel-quiet p-3">
            <p class="eyebrow">Commits</p>
            <p class="font-display text-xl text-emerald-300 mt-1">{{ bug.consensus_votes?.commit ?? 0 }}<span class="text-ink-500 text-sm">/9</span></p>
          </div>
        </div>
      </div>
    </section>

    <!-- Triage by analyzers -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Phase 1 · Analyzer triage</h3>
        <span class="font-mono text-[11px] text-ink-400">3 analyzers · root-cause</span>
      </div>
      <div class="panel-body grid grid-cols-1 md:grid-cols-3 gap-3">
        <div v-for="a in analyzers" :key="a.id" class="panel-quiet p-4 ring-analyzer">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-md bg-agent-analyzer flex items-center justify-center text-white font-mono text-[11px] font-bold">A</div>
              <p class="font-mono text-[11px] text-violet-300">{{ a.llm_provider }}</p>
            </div>
            <span class="font-mono text-[10px] text-ink-400">{{ a.avg_latency_ms }}ms</span>
          </div>
          <p class="text-[12.5px] text-ink-200 mt-3 leading-relaxed">
            <template v-if="a.llm_provider === 'anthropic'">Identified mutable shared state in {{ bug.bug_type.replace('_',' ') }} path. Fix locus: lines {{ bug.line_number - 1 }}–{{ bug.line_number + 2 }}.</template>
            <template v-else-if="a.llm_provider === 'openai'">Numeric precision issue. Trace shows float arithmetic on monetary values; recommend Decimal coercion at handler boundary.</template>
            <template v-else>Concurrent access detected via static call-graph analysis. Suggests transactional guard or per-resource lock.</template>
          </p>
          <div class="mt-3 flex items-center justify-between">
            <span class="font-mono text-[10px] text-ink-400">confidence</span>
            <div class="bar-track w-24"><div class="bar-fill bg-violet-400" :style="{ width: (60 + Math.random()*30) + '%' }"></div></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Healer debate + Diff -->
    <section class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="panel xl:col-span-1">
        <div class="panel-header">
          <h3 class="panel-title">Phase 2 · Healer proposals</h3>
          <span class="font-mono text-[11px] text-ink-400">3 candidates</span>
        </div>
        <div class="panel-body space-y-2">
          <button v-for="p in proposals" :key="p.agent.id"
            @click="selectedAgent = p.agent.id"
            :class="['w-full text-left p-3 rounded-lg border transition group',
              (activeProposal?.agent.id === p.agent.id)
                ? 'border-cyan-500/50 bg-cyan-500/5'
                : 'border-white/5 bg-ink-850/40 hover:border-white/10']">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-md bg-agent-healer flex items-center justify-center text-white font-mono text-[10px] font-bold">H</div>
                <span class="font-mono text-[11px] text-cyan-300">{{ p.agent.llm_provider }}</span>
              </div>
              <span :class="['status text-[10px]',
                p.result === 'accepted' ? 'status-resolved' : 'status-failed']">
                {{ p.result }}
              </span>
            </div>
            <p class="text-[12.5px] text-ink-100 font-medium mt-2">{{ p.label }}</p>
            <p class="text-[11.5px] text-ink-400 mt-1.5 leading-snug">{{ p.reasoning }}</p>
            <div class="mt-2 flex items-center justify-between">
              <span class="font-mono text-[10px] text-ink-400">confidence</span>
              <div class="flex items-center gap-2">
                <div class="bar-track w-20"><div class="bar-fill bg-cyan-400" :style="{ width: (p.confidence * 100) + '%' }"></div></div>
                <span class="font-mono text-[10px] text-cyan-300 w-8 text-right">{{ (p.confidence * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- Diff viewer -->
      <div class="panel xl:col-span-2">
        <div class="panel-header">
          <h3 class="panel-title">Diff · {{ activeProposal?.label || 'select a candidate' }}</h3>
          <div class="flex items-center gap-2">
            <span class="kbd">unified</span>
            <span :class="['status text-[10px]',
              activeProposal?.result === 'accepted' ? 'status-resolved' : 'status-failed']">
              {{ activeProposal?.result || '—' }}
            </span>
          </div>
        </div>
        <div class="panel-body p-0">
          <div class="code-block rounded-none border-0">
            <div class="code-head">
              <span>--- a/{{ bug.file_path }}</span>
              <span>+++ b/{{ bug.file_path }}</span>
            </div>
            <div class="py-2">
              <div v-for="(line, i) in diff" :key="i"
                :class="['diff-row',
                  line.type === 'add' ? 'diff-add' :
                  line.type === 'del' ? 'diff-del' :
                  line.type === 'hunk' ? 'diff-hunk' : 'diff-ctx']">
                <span class="text-ink-500 mr-3 select-none inline-block w-6 text-right">{{
                  line.type === 'add' ? '+' : line.type === 'del' ? '-' : line.type === 'hunk' ? '@' : ' '
                }}</span>{{ line.text }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Validator review -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Phase 3 · Validator sandbox review</h3>
        <span class="font-mono text-[11px] text-ink-400">3 validators · sandbox + tests</span>
      </div>
      <div class="panel-body grid grid-cols-1 md:grid-cols-3 gap-3">
        <div v-for="(v, i) in validators" :key="v.id" class="panel-quiet p-4 ring-validator">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-md bg-agent-validator flex items-center justify-center text-white font-mono text-[11px] font-bold">V</div>
              <p class="font-mono text-[11px] text-emerald-300">{{ v.llm_provider }}</p>
            </div>
            <span class="status status-resolved text-[10px]">passed</span>
          </div>
          <ul class="mt-3 space-y-1.5 text-[12px] text-ink-200">
            <li class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Compilation</li>
            <li class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Unit tests {{ 12 + i*3 }}/{{ 12 + i*3 }}</li>
            <li class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Regression suite</li>
            <li class="flex items-center gap-2"><span class="text-emerald-400">✓</span> Sandbox exit clean</li>
          </ul>
          <p class="font-mono text-[10px] text-ink-400 mt-3 leading-snug">
            "Fix preserves API contract; added precision invariant. Recommends merge."
          </p>
        </div>
      </div>
    </section>
  </div>

  <div v-else class="text-center py-24 text-ink-400">Bug not found</div>
</template>
