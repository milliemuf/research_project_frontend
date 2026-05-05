<script setup>
import { ref, computed, onMounted, onBeforeUnmount, reactive } from 'vue'
import api from '@/services/api'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const errorMessage = ref('IndexError: list index out of range')
const stackTrace = ref(`Traceback (most recent call last):
  File "main.py", line 8, in <module>
    assert sum_first_n([1, 2, 3, 4, 5], 5) == 15
  File "main.py", line 4, in sum_first_n
    total += xs[i]
IndexError: list index out of range`)
const originalCode = ref(`def sum_first_n(xs, n):
    total = 0
    for i in range(n + 1):    # bug
        total += xs[i]
    return total
`)
const fixedCode = ref(`def sum_first_n(xs, n):
    total = 0
    for i in range(n):
        total += xs[i]
    return total
`)
const explanation = ref('Replace range(n+1) with range(n) to stop one iteration earlier.')
const filePath = ref('main.py')
const lineNumber = ref(3)
const language = ref('python')
const confidence = ref(0.9)

const running = ref(false)
const result = ref(null)
const info = ref(null)
const elapsed = ref(0)
let elapsedTimer = null

// Live state, populated by WebSocket events
const live = reactive({
  runId: null,
  currentPhase: null,        // 'proposal' | 'validation' | 'pbft' | 'decided' | null
  validators: {},            // agent_id -> { status, model, is_valid, confidence, latency_ms, issues, reason }
  pbftSummary: null,         // { prepare_votes, commit_votes, quorum_required, duration_ms }
  decision: null,            // { success, decision, decision_reason, ... }
  log: [],                   // chronological event list for display
})

let ws = null

// Pre-canned demos so a viva audience can see different decisions
const PRESETS = [
  {
    name: 'Off-by-one (good fix)',
    error: 'IndexError: list index out of range',
    original: `def sum_first_n(xs, n):
    total = 0
    for i in range(n + 1):    # bug
        total += xs[i]
    return total
`,
    fixed: `def sum_first_n(xs, n):
    total = 0
    for i in range(n):
        total += xs[i]
    return total
`,
    explanation: 'Replace range(n+1) with range(n) to stop one iteration earlier.',
    confidence: 0.9,
  },
  {
    name: 'Off-by-one (DANGEROUS — uses eval)',
    error: 'IndexError: list index out of range',
    original: `def sum_first_n(xs, n):
    return sum(xs[i] for i in range(n + 1))
`,
    fixed: `def sum_first_n(xs, n):
    return eval(f"sum({xs[:n]})")
`,
    explanation: 'Use eval to compute the sum dynamically.',
    confidence: 0.6,
  },
  {
    name: 'None-check missing (good fix)',
    error: "AttributeError: 'NoneType' object has no attribute 'upper'",
    original: `def greet(name):
    return name.upper()
`,
    fixed: `def greet(name):
    if name is None:
        return ''
    return name.upper()
`,
    explanation: 'Guard against None before calling upper().',
    confidence: 0.92,
  },
]

// ---------------------------------------------------------------------------
// WebSocket plumbing
// ---------------------------------------------------------------------------
function buildWsUrl() {
  // VITE_WS_URL is the base ('ws://127.0.0.1:7222/ws/live'); add channel filter
  const base = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:7222/ws/live'
  const sep = base.includes('?') ? '&' : '?'
  return `${base}${sep}channel=consensus`
}

function openWs() {
  try {
    ws = new WebSocket(buildWsUrl())
    ws.onmessage = (msg) => {
      let payload
      try { payload = JSON.parse(msg.data) } catch { return }
      if (!payload || !payload.event) return
      handleEvent(payload)
    }
    ws.onclose = () => {
      // Auto-reconnect after 2s, but only while the page is mounted
      if (ws !== null) {
        setTimeout(() => { if (ws !== null) openWs() }, 2000)
      }
    }
    ws.onerror = () => { /* fall back silently to non-streamed mode */ }
  } catch (e) {
    ws = null
  }
}

function handleEvent(payload) {
  // Only react to events for our current run
  if (payload.run_id && live.runId && payload.run_id !== live.runId) return

  const { event, data } = payload
  // Append to chronological log (for the events panel)
  live.log.push({ time: new Date().toLocaleTimeString(), event, data })
  if (live.log.length > 40) live.log.shift()

  switch (event) {
    case 'lab_run_started':
      live.currentPhase = 'proposal'
      // Pre-populate validator slots so they animate from "pending"
      for (const agent_id of (data.agents || [])) {
        if (!live.validators[agent_id]) {
          live.validators[agent_id] = { agent_id, status: 'pending' }
        }
      }
      break
    case 'phase_finished':
      if (data.phase === 'proposal') live.currentPhase = 'validation'
      if (data.phase === 'validation') live.currentPhase = 'pbft'
      if (data.phase === 'pbft') {
        live.currentPhase = 'decided'
        live.pbftSummary = {
          prepare_votes: data.prepare_votes,
          commit_votes: data.commit_votes,
          quorum_required: data.quorum_required,
          duration_ms: data.duration_ms,
        }
      }
      break
    case 'phase_started':
      live.currentPhase = data.phase
      break
    case 'validator_started':
      live.validators[data.agent_id] = {
        ...(live.validators[data.agent_id] || {}),
        agent_id: data.agent_id,
        model: data.model,
        status: 'running',
      }
      break
    case 'validator_finished':
      live.validators[data.agent_id] = {
        ...(live.validators[data.agent_id] || {}),
        agent_id: data.agent_id,
        status: 'voted',
        is_valid: data.is_valid,
        confidence: data.confidence,
        latency_ms: data.latency_ms,
        issues: data.issues || [],
        reason: data.reason || '',
      }
      break
    case 'validator_failed':
      live.validators[data.agent_id] = {
        ...(live.validators[data.agent_id] || {}),
        agent_id: data.agent_id,
        status: 'failed',
        error: data.error,
      }
      break
    case 'lab_run_decided':
      live.currentPhase = 'decided'
      live.decision = data
      break
  }
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------
async function loadInfo() {
  try {
    info.value = (await api.get('/api/v1/consensus-lab/info')).data
  } catch (e) {
    info.value = null
  }
}

function resetLive(runId) {
  live.runId = runId
  live.currentPhase = null
  live.validators = {}
  live.pbftSummary = null
  live.decision = null
  live.log = []
}

function newRunId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID()
  return 'run-' + Math.random().toString(36).slice(2) + '-' + Date.now().toString(36)
}

async function runConsensus() {
  if (running.value) return
  running.value = true
  result.value = null
  elapsed.value = 0
  const runId = newRunId()
  resetLive(runId)
  const startedAt = Date.now()
  elapsedTimer = setInterval(() => { elapsed.value = Date.now() - startedAt }, 50)
  try {
    const resp = await api.post('/api/v1/consensus-lab/run', {
      client_request_id: runId,
      error_message: errorMessage.value,
      stack_trace: stackTrace.value,
      original_code: originalCode.value,
      fixed_code: fixedCode.value,
      explanation: explanation.value,
      file_path: filePath.value,
      line_number: Number(lineNumber.value),
      language: language.value,
      confidence_score: Number(confidence.value),
    })
    result.value = resp.data
    await loadInfo()
  } catch (e) {
    result.value = {
      success: false,
      decision: 'error',
      decision_reason: e?.response?.data?.detail || e?.message || 'request failed',
      sequence: -1,
      view: 0,
      quorum_required: 0,
      prepare_votes: 0,
      commit_votes: 0,
      duration_ms: 0,
      phases: [],
      votes: [],
      timestamp: new Date().toISOString(),
    }
  } finally {
    running.value = false
    if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null }
  }
}

function loadPreset(p) {
  errorMessage.value = p.error
  originalCode.value = p.original
  fixedCode.value = p.fixed
  explanation.value = p.explanation
  confidence.value = p.confidence
  result.value = null
  resetLive(null)
}

const recent = computed(() => info.value?.recent_runs ?? [])
const agentRoster = computed(() => info.value?.registered_agents ?? [])
const quorum = computed(() => info.value?.quorum ?? 3)
const nRequired = computed(() => info.value?.n_required ?? 4)

// Live state derived
const liveValidatorList = computed(() => Object.values(live.validators))
const PHASE_ORDER = ['proposal', 'validation', 'pbft', 'decided']
function phaseClass(p) {
  if (!live.currentPhase) return 'opacity-30'
  const cur = PHASE_ORDER.indexOf(live.currentPhase)
  const me = PHASE_ORDER.indexOf(p)
  if (me < cur) return 'text-emerald-300 ring-emerald-500/40 bg-emerald-500/10'
  if (me === cur) return 'text-cyan-200 ring-cyan-400/60 bg-cyan-500/15 animate-pulse'
  return 'text-ink-500 ring-white/5 bg-ink-900/40'
}

onMounted(() => {
  loadInfo()
  openWs()
})

onBeforeUnmount(() => {
  const w = ws
  ws = null
  try { w?.close() } catch {}
  if (elapsedTimer) clearInterval(elapsedTimer)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="panel p-6">
      <div class="flex items-start justify-between flex-wrap gap-4">
        <div>
          <p class="eyebrow">Live PBFT consensus on a candidate fix</p>
          <h2 class="font-display text-2xl text-ink-100 mt-2">Consensus Lab</h2>
          <p class="text-ink-300 text-sm mt-2 max-w-2xl">
            Paste a buggy snippet and a candidate fix. Four heterogeneous Ollama validators
            evaluate it independently, then PBFT runs its three phases (pre-prepare, prepare,
            commit). Approval requires {{ quorum }} of {{ nRequired }} agents to agree.
            Phase events stream over WebSocket so you can watch each validator vote live.
          </p>
        </div>
        <div class="text-right">
          <p class="eyebrow">PBFT config</p>
          <p class="font-mono text-lg mt-1 text-ink-100">f = 1, quorum = {{ quorum }}/{{ nRequired }}</p>
          <p class="font-mono text-[10px] text-ink-400 mt-1">classical PBFT three-phase</p>
        </div>
      </div>

      <!-- Phase pulse strip -->
      <div class="mt-5 grid grid-cols-4 gap-2">
        <div v-for="p in ['proposal', 'validation', 'pbft', 'decided']" :key="p"
          :class="['rounded-lg ring-1 px-3 py-2 transition-all duration-300', phaseClass(p)]">
          <p class="font-mono text-[10px] uppercase tracking-wider">{{ p === 'pbft' ? 'PBFT 3-phase' : p }}</p>
          <p class="font-mono text-[11px] mt-1">
            <span v-if="p === 'proposal'">stage proposal</span>
            <span v-else-if="p === 'validation'">{{ liveValidatorList.length || nRequired }} validators</span>
            <span v-else-if="p === 'pbft'">pre-prepare → prepare → commit</span>
            <span v-else>final decision</span>
          </p>
        </div>
      </div>

      <!-- Agent roster -->
      <div v-if="agentRoster.length" class="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div v-for="a in agentRoster" :key="a.agent_id"
          class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
          <p class="font-mono text-[11px] text-ink-300 truncate">{{ a.agent_id }}</p>
          <p class="font-mono text-[10px] text-ink-400 mt-0.5">{{ a.model_name }}</p>
          <div class="mt-1 bar-track">
            <div class="bar-fill bg-gradient-to-r from-violet-400 via-brand-400 to-cyan-400"
                 :style="{ width: (a.reputation * 100) + '%' }"></div>
          </div>
          <p class="font-mono text-[10px] text-ink-400 mt-0.5">
            rep {{ (a.reputation * 100).toFixed(0) }}% · {{ a.total_tasks }} tasks
          </p>
        </div>
      </div>

      <!-- Preset buttons -->
      <div class="mt-5 flex flex-wrap gap-2">
        <span class="eyebrow self-center pr-2">Presets:</span>
        <button v-for="p in PRESETS" :key="p.name" @click="loadPreset(p)"
          class="px-3 py-1 rounded-md text-[12px] font-mono ring-1 ring-white/10 bg-white/[0.03] text-ink-200 hover:bg-white/[0.08] transition">
          {{ p.name }}
        </button>
      </div>
    </section>

    <!-- Editor + Live View -->
    <section class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <!-- Inputs -->
      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">Bug context &amp; candidate fix</h3>
          <span class="font-mono text-[11px] text-ink-400">propose this to the consensus engine</span>
        </div>
        <div class="panel-body space-y-3">
          <label class="block text-[12px] text-ink-300">
            Error message
            <input v-model="errorMessage"
              class="mt-1 w-full bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-ink-100" />
          </label>
          <label class="block text-[12px] text-ink-300">
            Stack trace
            <textarea v-model="stackTrace" rows="3"
              class="mt-1 w-full bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[11px] text-ink-100 resize-none"></textarea>
          </label>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label class="block text-[12px] text-ink-300">
              Original (buggy) code
              <textarea v-model="originalCode" rows="6" spellcheck="false"
                class="mt-1 w-full bg-ink-950 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-rose-200 resize-none"></textarea>
            </label>
            <label class="block text-[12px] text-ink-300">
              Candidate fixed code
              <textarea v-model="fixedCode" rows="6" spellcheck="false"
                class="mt-1 w-full bg-ink-950 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-emerald-200 resize-none"></textarea>
            </label>
          </div>

          <label class="block text-[12px] text-ink-300">
            Explanation
            <input v-model="explanation"
              class="mt-1 w-full bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-ink-100" />
          </label>

          <div class="grid grid-cols-3 gap-3">
            <label class="text-[12px] text-ink-300">
              File
              <input v-model="filePath"
                class="mt-1 w-full bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-ink-100" />
            </label>
            <label class="text-[12px] text-ink-300">
              Line
              <input v-model.number="lineNumber" type="number" min="1"
                class="mt-1 w-full bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-ink-100" />
            </label>
            <label class="text-[12px] text-ink-300">
              Confidence
              <input v-model.number="confidence" type="number" step="0.05" min="0" max="1"
                class="mt-1 w-full bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-ink-100" />
            </label>
          </div>

          <div class="flex items-center justify-between pt-1">
            <p v-if="running" class="font-mono text-[11px] text-ink-400">
              elapsed: {{ (elapsed / 1000).toFixed(2) }}s · waiting for {{ nRequired }} validators…
            </p>
            <p v-else class="font-mono text-[10px] text-ink-400">
              click run to invoke validators + PBFT
            </p>
            <button @click="runConsensus" :disabled="running"
              class="px-4 py-2 rounded-lg font-medium text-[13px] transition
                     bg-gradient-to-r from-violet-500 to-cyan-500 text-white
                     hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed">
              <span v-if="!running">▶ Propose to consensus</span>
              <span v-else class="flex items-center gap-2">
                <span class="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin"></span>
                Running…
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Live view (during run) and final result (after) -->
      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">{{ running ? 'Live consensus stream' : 'Consensus result' }}</h3>
          <span v-if="result" class="font-mono text-[11px] uppercase tracking-wider"
            :class="result.success ? 'text-emerald-300' : 'text-rose-300'">
            {{ result.decision }}
          </span>
          <span v-else-if="running && live.runId" class="font-mono text-[11px] text-cyan-300 animate-pulse">
            ◉ live · {{ live.currentPhase || 'starting' }}
          </span>
        </div>
        <div class="panel-body space-y-3">
          <!-- Empty state -->
          <div v-if="!result && !running"
            class="text-ink-400 text-sm py-12 text-center font-mono">
            Run a proposal to see the consensus phases stream live.
          </div>

          <!-- LIVE: validator state machine while running -->
          <div v-if="running" class="space-y-3">
            <p class="eyebrow">Validators</p>
            <div class="space-y-2">
              <div v-for="agentId in agentRoster.map(a => a.agent_id)" :key="agentId"
                class="rounded-lg ring-1 px-3 py-2 transition-all duration-200"
                :class="(() => {
                  const v = live.validators[agentId]
                  if (!v || v.status === 'pending') return 'ring-white/5 bg-ink-900/40'
                  if (v.status === 'running') return 'ring-cyan-400/40 bg-cyan-500/[0.06] animate-pulse'
                  if (v.status === 'failed') return 'ring-rose-500/30 bg-rose-500/[0.05]'
                  return v.is_valid ? 'ring-emerald-500/30 bg-emerald-500/[0.05]' : 'ring-rose-500/30 bg-rose-500/[0.05]'
                })()">
                <div class="flex items-center gap-3">
                  <span class="font-mono text-[12px] text-ink-100 truncate flex-1">{{ agentId }}</span>
                  <span class="font-mono text-[10px] text-ink-400">
                    {{ live.validators[agentId]?.model || agentRoster.find(a => a.agent_id === agentId)?.model_name }}
                  </span>
                  <span v-if="!live.validators[agentId] || live.validators[agentId].status === 'pending'"
                    class="font-mono text-[11px] text-ink-400">⏳ pending</span>
                  <span v-else-if="live.validators[agentId].status === 'running'"
                    class="font-mono text-[11px] text-cyan-300">◉ thinking…</span>
                  <span v-else-if="live.validators[agentId].status === 'failed'"
                    class="font-mono text-[11px] text-rose-300">✗ error</span>
                  <template v-else>
                    <span class="font-mono text-[11px]"
                      :class="live.validators[agentId].is_valid ? 'text-emerald-300' : 'text-rose-300'">
                      {{ live.validators[agentId].is_valid ? '✓ approve' : '✗ reject' }}
                    </span>
                    <span class="font-mono text-[11px] text-ink-300">
                      {{ ((live.validators[agentId].confidence || 0) * 100).toFixed(0) }}%
                    </span>
                    <span class="font-mono text-[11px] text-cyan-300">{{ Math.round(live.validators[agentId].latency_ms || 0) }} ms</span>
                  </template>
                </div>
                <p v-if="live.validators[agentId]?.issues?.length" class="font-mono text-[10px] text-rose-200 mt-1">
                  issues: {{ live.validators[agentId].issues.slice(0, 2).join(' · ') }}
                </p>
              </div>
            </div>

            <!-- Live PBFT summary as it lights up -->
            <div v-if="live.pbftSummary" class="rounded-lg ring-1 ring-cyan-400/30 bg-cyan-500/[0.05] px-3 py-2">
              <p class="eyebrow">PBFT votes</p>
              <p class="font-mono text-[12px] mt-1 text-ink-100">
                prepare {{ live.pbftSummary.prepare_votes }}/{{ live.pbftSummary.quorum_required }} ·
                commit {{ live.pbftSummary.commit_votes }}/{{ live.pbftSummary.quorum_required }} ·
                {{ Math.round(live.pbftSummary.duration_ms) }} ms
              </p>
            </div>

            <!-- Live event log -->
            <details class="rounded-lg ring-1 ring-white/5 bg-ink-900/40">
              <summary class="px-3 py-2 cursor-pointer font-mono text-[11px] text-ink-400 hover:text-ink-100">
                ◉ event log ({{ live.log.length }} events)
              </summary>
              <div class="px-3 py-1 max-h-64 overflow-y-auto space-y-0.5">
                <div v-for="(e, i) in [...live.log].reverse()" :key="i"
                  class="font-mono text-[10px] text-ink-300 flex gap-2">
                  <span class="text-ink-500 w-16 shrink-0">{{ e.time }}</span>
                  <span class="text-cyan-300 w-32 shrink-0">{{ e.event }}</span>
                  <span class="text-ink-400 truncate">{{ JSON.stringify(e.data).slice(0, 80) }}</span>
                </div>
              </div>
            </details>
          </div>

          <!-- POST-RUN: full result -->
          <div v-if="result && !running" class="space-y-4">
            <div class="rounded-lg ring-1 px-4 py-3"
              :class="result.success
                ? 'ring-emerald-500/30 bg-emerald-500/5'
                : 'ring-rose-500/30 bg-rose-500/5'">
              <div class="flex items-center justify-between">
                <div>
                  <p class="eyebrow">Decision</p>
                  <p class="font-display text-xl mt-1"
                    :class="result.success ? 'text-emerald-300' : 'text-rose-300'">
                    {{ result.success ? '✓ APPROVED' : '✗ REJECTED' }}
                  </p>
                </div>
                <div class="text-right">
                  <p class="eyebrow">Total time</p>
                  <p class="font-mono text-lg mt-1 text-ink-100">{{ result.duration_ms.toFixed(0) }} ms</p>
                </div>
              </div>
              <p class="font-mono text-[12px] text-ink-300 mt-2">{{ result.decision_reason }}</p>
            </div>

            <div class="grid grid-cols-3 gap-2">
              <div class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
                <p class="eyebrow">prepare</p>
                <p class="font-mono text-lg mt-0.5"
                   :class="result.prepare_votes >= result.quorum_required ? 'text-emerald-300' : 'text-rose-300'">
                  {{ result.prepare_votes }} / {{ result.quorum_required }}
                </p>
              </div>
              <div class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
                <p class="eyebrow">commit</p>
                <p class="font-mono text-lg mt-0.5"
                   :class="result.commit_votes >= result.quorum_required ? 'text-emerald-300' : 'text-rose-300'">
                  {{ result.commit_votes }} / {{ result.quorum_required }}
                </p>
              </div>
              <div class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
                <p class="eyebrow">sequence</p>
                <p class="font-mono text-lg mt-0.5 text-ink-100">{{ result.sequence }}</p>
              </div>
            </div>

            <div>
              <p class="eyebrow mb-2">Phase timeline</p>
              <div class="space-y-1">
                <div v-for="(p, i) in result.phases" :key="i"
                  class="flex items-center gap-3 rounded-md ring-1 ring-white/5 bg-ink-900/40 px-3 py-1.5">
                  <span class="font-mono text-[10px] text-ink-400 w-20 uppercase tracking-wider">{{ p.phase }}</span>
                  <span class="font-mono text-[11px] text-ink-300 flex-1">{{ p.description }}</span>
                  <span class="font-mono text-[11px] text-cyan-300">{{ p.duration_ms.toFixed(0) }} ms</span>
                </div>
              </div>
            </div>

            <div>
              <p class="eyebrow mb-2">Per-agent votes</p>
              <div class="space-y-2">
                <div v-for="v in result.votes" :key="v.agent_id"
                  class="rounded-lg ring-1 px-3 py-2"
                  :class="v.is_valid ? 'ring-emerald-500/20 bg-emerald-500/[0.03]' : 'ring-rose-500/20 bg-rose-500/[0.03]'">
                  <div class="flex items-center gap-3">
                    <span class="font-mono text-[12px] text-ink-100 truncate flex-1">{{ v.agent_id }}</span>
                    <span class="font-mono text-[11px]"
                      :class="v.is_valid ? 'text-emerald-300' : 'text-rose-300'">
                      {{ v.is_valid ? '✓ approve' : '✗ reject' }}
                    </span>
                    <span class="font-mono text-[11px] text-ink-300">conf {{ (v.confidence * 100).toFixed(0) }}%</span>
                    <span class="font-mono text-[11px] text-cyan-300">{{ v.latency_ms.toFixed(0) }} ms</span>
                  </div>
                  <p v-if="v.issues.length" class="font-mono text-[10px] text-rose-200 mt-1">
                    issues: {{ v.issues.slice(0, 3).join(' · ') }}
                  </p>
                  <p v-else-if="v.reason" class="font-mono text-[10px] text-ink-400 mt-1 truncate">
                    {{ v.reason }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent runs -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Recent consensus runs</h3>
        <span class="font-mono text-[11px] text-ink-400">last {{ recent.length }} of 20</span>
      </div>
      <div class="panel-body p-0">
        <div v-if="!recent.length" class="text-ink-400 text-sm py-8 text-center font-mono">
          No runs yet.
        </div>
        <table v-else class="w-full text-[12px]">
          <thead class="bg-white/[0.02] text-ink-400 font-mono">
            <tr>
              <th class="px-4 py-2 text-left font-normal">timestamp</th>
              <th class="px-4 py-2 text-left font-normal">bug id</th>
              <th class="px-4 py-2 text-left font-normal">decision</th>
              <th class="px-4 py-2 text-right font-normal">prepare</th>
              <th class="px-4 py-2 text-right font-normal">commit</th>
              <th class="px-4 py-2 text-right font-normal">duration</th>
              <th class="px-4 py-2 text-left font-normal">reason</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in recent" :key="i" class="border-t border-white/5 hover:bg-white/[0.02]">
              <td class="px-4 py-1.5 font-mono text-ink-300">{{ new Date(r.timestamp).toLocaleTimeString() }}</td>
              <td class="px-4 py-1.5 font-mono text-ink-200 truncate max-w-[160px]">{{ r.bug_id }}</td>
              <td class="px-4 py-1.5">
                <span :class="r.decision === 'approved' ? 'text-emerald-300' : 'text-rose-300'" class="font-mono uppercase tracking-wider">
                  {{ r.decision }}
                </span>
              </td>
              <td class="px-4 py-1.5 text-right font-mono text-ink-200">{{ r.prepare_votes }} / {{ r.quorum_required }}</td>
              <td class="px-4 py-1.5 text-right font-mono text-ink-200">{{ r.commit_votes }} / {{ r.quorum_required }}</td>
              <td class="px-4 py-1.5 text-right font-mono text-ink-200">{{ r.duration_ms }} ms</td>
              <td class="px-4 py-1.5 font-mono text-ink-400 truncate max-w-md">{{ r.decision_reason }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
