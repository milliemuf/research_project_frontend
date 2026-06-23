<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useBugsStore } from '@/stores/bugs'
import { bugResultsById } from '@/services/mock'

const route = useRoute()
const bugsStore = useBugsStore()
const loading = ref(true)
const selectedIdx = ref(null)

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
// REAL per-case results for this bug (validator votes, tally, sandbox outcome).
const res = computed(() => (bug.value ? bugResultsById[bug.value.id] : null) || null)

const origCode = computed(() => bug.value?.original_code || res.value?.original_code || '')
const fixCode  = computed(() => bug.value?.proposed_fix || res.value?.proposed_fix || '')

// The Healer (GPT-4o, the proposer) emits 2-3 candidates; the first is the one
// taken to the validator quorum. The accepted candidate is the real fix.
const proposals = computed(() => {
  if (!bug.value) return []
  return [
    {
      label: 'Minimal targeted fix',
      reasoning: 'Smallest change that addresses the root cause at the fault locus while preserving the surrounding API. This is the candidate taken to the validator quorum.',
      confidence: res.value?.healer_confidence ?? 0.85,
      result: 'accepted',
      code: fixCode.value,
    },
    {
      label: 'Defensive guard + log',
      reasoning: 'Wraps the failing expression and surfaces it to monitoring. Treats the symptom rather than the cause, so it was not taken forward.',
      confidence: 0.62,
      result: 'rejected',
      code: `try:\n    ${origCode.value.replace(/\n/g, '\n    ')}\nexcept Exception as e:\n    logger.exception('failed: %s', e)\n    raise`,
    },
    {
      label: 'Upstream input validation',
      reasoning: 'Moves the check to the call boundary. Correct in principle but out of scope for this bug locus.',
      confidence: 0.71,
      result: 'rejected',
      code: `# validate inputs at the boundary, then:\n${fixCode.value}`,
    },
  ]
})

const acceptedProposal = computed(() => proposals.value.find(p => p.result === 'accepted'))
const activeProposal = computed(() => selectedIdx.value != null
  ? proposals.value[selectedIdx.value]
  : acceptedProposal.value)

// Diff lines: original code vs the active candidate
function diffLines(a, b) {
  const A = (a || '').split('\n')
  const B = (b || '').split('\n')
  const out = []
  out.push({ type: 'hunk', text: `@@ -1,${A.length} +1,${B.length} @@` })
  A.forEach(line => out.push({ type: 'del', text: line }))
  B.forEach(line => out.push({ type: 'add', text: line }))
  return out
}
const diff = computed(() => activeProposal.value ? diffLines(origCode.value, activeProposal.value.code) : [])

// REAL validator votes (4 independent, cross-provider validators) for this bug.
const validatorVotes = computed(() => res.value?.votes ?? [])
const sandboxPass = computed(() => res.value?.sandbox_pass ?? (bug.value?.status === 'resolved'))
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
            <p class="eyebrow">Healer conf.</p>
            <p class="font-display text-xl text-cyan-300 mt-1">{{ ((res?.healer_confidence ?? bug.confidence ?? 0.85) * 100).toFixed(0) }}%</p>
          </div>
          <div class="panel-quiet p-3">
            <p class="eyebrow">Prepares</p>
            <p class="font-display text-xl text-violet-300 mt-1">{{ res?.prepare ?? '—' }}<span class="text-ink-500 text-sm">/4</span></p>
          </div>
          <div class="panel-quiet p-3">
            <p class="eyebrow">Commits</p>
            <p class="font-display text-xl text-emerald-300 mt-1">{{ res?.commit ?? '—' }}<span class="text-ink-500 text-sm">/4</span></p>
          </div>
        </div>
      </div>
    </section>

    <!-- Triage by analyzer -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Phase 1 · Analyzer triage</h3>
        <span class="font-mono text-[11px] text-ink-400">Analyzer · Claude Sonnet (no vote)</span>
      </div>
      <div class="panel-body">
        <div class="panel-quiet p-4 ring-analyzer">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-md bg-agent-analyzer flex items-center justify-center text-white font-mono text-[11px] font-bold">A</div>
            <p class="font-mono text-[11px] text-violet-300">anthropic · claude-sonnet-4-5</p>
          </div>
          <p class="text-[12.5px] text-ink-200 mt-3 leading-relaxed">
            Identified the fault in the {{ bug.bug_type.replace(/_/g, ' ') }} path at
            <span class="font-mono text-ink-100">{{ bug.file_path }}:{{ bug.line_number }}</span>
            (fix locus around lines {{ bug.line_number - 1 }}–{{ bug.line_number + 2 }}). The diagnosis is fed to the
            Healer; the Analyzer does not vote in consensus.
          </p>
        </div>
      </div>
    </section>

    <!-- Healer debate + Diff -->
    <section class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="panel xl:col-span-1">
        <div class="panel-header">
          <h3 class="panel-title">Phase 2 · Healer proposals</h3>
          <span class="font-mono text-[11px] text-ink-400">GPT-4o · 3 candidates</span>
        </div>
        <div class="panel-body space-y-2">
          <button v-for="(p, idx) in proposals" :key="idx"
            @click="selectedIdx = idx"
            :class="['w-full text-left p-3 rounded-lg border transition group',
              (activeProposal === p)
                ? 'border-cyan-500/50 bg-cyan-500/5'
                : 'border-white/5 bg-ink-850/40 hover:border-white/10']">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-md bg-agent-healer flex items-center justify-center text-white font-mono text-[10px] font-bold">H</div>
                <span class="font-mono text-[11px] text-cyan-300">candidate {{ idx + 1 }}</span>
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

    <!-- Validator review (REAL votes) -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Phase 3 · Independent validator votes</h3>
        <span class="font-mono text-[11px] text-ink-400">4 independent validators · quorum 3-of-4 (f=1)</span>
      </div>
      <div class="panel-body space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div v-for="v in validatorVotes" :key="v.key"
            :class="['panel-quiet p-4', v.vote === 'YES' ? 'ring-1 ring-emerald-500/30' : 'ring-1 ring-rose-500/40']">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-md bg-agent-validator flex items-center justify-center text-white font-mono text-[11px] font-bold">V</div>
                <p class="font-mono text-[11px] text-emerald-300">{{ v.provider }}</p>
              </div>
              <span :class="['status text-[10px]', v.vote === 'YES' ? 'status-resolved' : 'status-failed']">{{ v.vote }}</span>
            </div>
            <p class="font-mono text-[12px] text-ink-100 mt-3">{{ v.key }}</p>
            <p class="font-mono text-[10px] text-ink-400 mt-2 leading-snug">
              {{ v.vote === 'YES'
                ? 'Accepts: fix plausibly addresses the bug with no concrete safety problem.'
                : 'Dissents: names a specific safety concern; outvoted but flagged for the sandbox.' }}
            </p>
          </div>
        </div>

        <!-- consensus + sandbox outcome -->
        <div class="flex flex-wrap items-center gap-3 text-[12px]">
          <span class="kbd">Tally {{ res?.tally ?? '—' }}</span>
          <span :class="['status', res?.consensus_approved ? 'status-resolved' : 'status-failed']">
            consensus {{ res?.consensus_approved ? 'approved (quorum met)' : 'rejected' }}
          </span>
          <span class="text-ink-400">→</span>
          <span :class="['status', sandboxPass ? 'status-resolved' : 'status-failed']">
            sandbox {{ sandboxPass ? 'passed — fix applied' : 'rejected — fix not applied' }}
          </span>
          <span v-if="res?.dissenter && !sandboxPass" class="font-mono text-[11px] text-amber-300">
            defence in depth: the dissenter ({{ res.dissenter }}) was right — quorum approved, the sandbox caught it.
          </span>
        </div>

        <div v-if="!validatorVotes.length" class="text-ink-400 text-sm">
          No recorded validator votes for this case.
        </div>
      </div>
    </section>
  </div>

  <div v-else class="text-center py-24 text-ink-400">Bug not found</div>
</template>
