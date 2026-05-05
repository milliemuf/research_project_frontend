<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const code = ref(`# Run any Python snippet in the isolated sandbox.
# Sandbox staging dir is destroyed after each run.

def safe_div(a, b):
    if b == 0:
        return 0
    return a / b

if __name__ == '__main__':
    assert safe_div(10, 2) == 5
    assert safe_div(10, 0) == 0
    print('ok')
`)
const language = ref('python')
const timeoutS = ref(15)
const customCommand = ref('')

const running = ref(false)
const result = ref(null)
const info = ref(null)

// Pre-canned synthetic snippets so demos are one click away
const SAMPLES = [
  {
    name: 'Off-by-one (passes)',
    language: 'python',
    code: `def sum_first_n(xs, n):
    total = 0
    for i in range(n):
        total += xs[i]
    return total

if __name__ == '__main__':
    assert sum_first_n([1, 2, 3, 4, 5], 5) == 15
    print('ok')
`,
  },
  {
    name: 'Off-by-one (BUGGY)',
    language: 'python',
    code: `def sum_first_n(xs, n):
    total = 0
    for i in range(n + 1):    # bug: range goes one past
        total += xs[i]
    return total

if __name__ == '__main__':
    assert sum_first_n([1, 2, 3, 4, 5], 5) == 15
    print('ok')
`,
  },
  {
    name: 'Mutable default arg (BUGGY)',
    language: 'python',
    code: `def append(item, bucket=[]):
    bucket.append(item)
    return bucket

if __name__ == '__main__':
    assert append(1) == [1]
    assert append(2) == [2], 'append leaks across calls'
    print('ok')
`,
  },
  {
    name: 'Hello world (JS)',
    language: 'javascript',
    code: `console.log("hello from node");
process.exit(0);
`,
  },
]

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------
async function loadInfo() {
  try {
    info.value = (await api.get('/api/v1/sandbox/info')).data
  } catch (e) {
    info.value = null
  }
}

async function runSandbox() {
  if (!code.value.trim()) return
  running.value = true
  result.value = null
  try {
    const payload = {
      code: code.value,
      language: language.value,
      timeout_s: Number(timeoutS.value),
    }
    if (customCommand.value.trim()) {
      payload.test_command = customCommand.value.trim().split(/\s+/)
    }
    const resp = await api.post('/api/v1/sandbox/run', payload)
    result.value = resp.data
    await loadInfo()  // refresh recent runs list
  } catch (e) {
    result.value = {
      success: false,
      backend: 'error',
      exit_code: -1,
      duration_ms: 0,
      timed_out: false,
      stdout: '',
      stderr: e?.response?.data?.detail || e?.message || 'request failed',
      tests_passed: null,
      tests_failed: null,
      error: 'frontend_error',
      timestamp: new Date().toISOString(),
      short_reason: 'request failed',
    }
  } finally {
    running.value = false
  }
}

function loadSample(s) {
  code.value = s.code
  language.value = s.language
  customCommand.value = ''
  result.value = null
}

const recentRuns = computed(() => info.value?.recent_runs ?? [])
const activeBackend = computed(() => info.value?.active_backend ?? 'unknown')
const supportedLangs = computed(() => info.value?.supported_languages ?? ['python', 'javascript', 'java'])

onMounted(loadInfo)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="panel p-6">
      <div class="flex items-start justify-between flex-wrap gap-4">
        <div>
          <p class="eyebrow">Live execution surface</p>
          <h2 class="font-display text-2xl text-ink-100 mt-2">Sandbox</h2>
          <p class="text-ink-300 text-sm mt-2 max-w-2xl">
            Stage any candidate fix and run it inside the isolated sandbox.
            Docker is preferred; subprocess is used as a fallback when Docker is unavailable.
            The sandbox is the same one the H-BFT pipeline uses to validate a consensus-approved fix
            before applying it.
          </p>
        </div>
        <div class="text-right">
          <p class="eyebrow">Active backend</p>
          <p class="font-mono text-lg mt-1"
             :class="activeBackend === 'docker' ? 'text-emerald-300' : activeBackend === 'subprocess' ? 'text-amber-300' : 'text-ink-400'">
            {{ activeBackend }}
          </p>
          <p v-if="info" class="font-mono text-[10px] text-ink-400">
            timeout {{ info.default_timeout_s }}s · mem {{ info.memory_limit }} · cpu {{ info.cpu_limit }}
          </p>
        </div>
      </div>

      <!-- Sample selector -->
      <div class="mt-5 flex flex-wrap gap-2">
        <span class="eyebrow self-center pr-2">Quick samples:</span>
        <button v-for="s in SAMPLES" :key="s.name" @click="loadSample(s)"
          class="px-3 py-1 rounded-md text-[12px] font-mono ring-1 ring-white/10 bg-white/[0.03] text-ink-200 hover:bg-white/[0.08] transition">
          {{ s.name }}
        </button>
      </div>
    </section>

    <!-- Editor + Result -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Editor -->
      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">Code</h3>
          <span class="font-mono text-[11px] text-ink-400">staged into a one-shot work dir</span>
        </div>
        <div class="panel-body space-y-3">
          <div class="flex flex-wrap items-center gap-3">
            <label class="text-[12px] text-ink-300">
              Language:
              <select v-model="language"
                class="ml-2 bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-ink-100">
                <option v-for="l in supportedLangs" :key="l" :value="l">{{ l }}</option>
              </select>
            </label>
            <label class="text-[12px] text-ink-300">
              Timeout:
              <input v-model.number="timeoutS" type="number" min="1" max="120"
                class="ml-2 w-16 bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-ink-100" />
              <span class="ml-1 text-ink-400">s</span>
            </label>
            <label class="text-[12px] text-ink-300 flex-1 min-w-[200px]">
              Custom run command (optional):
              <input v-model="customCommand" type="text" placeholder="python -m pytest -q"
                class="mt-1 w-full bg-ink-900 ring-1 ring-white/10 rounded-md px-2 py-1 font-mono text-[12px] text-ink-100" />
            </label>
          </div>

          <textarea v-model="code" spellcheck="false"
            class="w-full h-[440px] bg-ink-950 text-ink-100 font-mono text-[13px] leading-snug
                   rounded-lg ring-1 ring-white/10 px-4 py-3 resize-none focus:outline-none focus:ring-brand-400/40"></textarea>

          <div class="flex items-center justify-between">
            <p class="font-mono text-[10px] text-ink-400">
              {{ code.length.toLocaleString() }} chars · sandbox tears down after run
            </p>
            <button @click="runSandbox" :disabled="running"
              class="px-4 py-2 rounded-lg font-medium text-[13px] transition
                     bg-gradient-to-r from-violet-500 to-cyan-500 text-white
                     hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed">
              <span v-if="!running">▶ Run in sandbox</span>
              <span v-else class="flex items-center gap-2">
                <span class="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin"></span>
                Running…
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Result -->
      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">Result</h3>
          <span v-if="result" class="font-mono text-[11px]"
            :class="result.success ? 'text-emerald-300' : 'text-rose-300'">
            {{ result.success ? '✓ passed' : '✗ failed' }} · {{ result.backend }}
          </span>
        </div>
        <div class="panel-body space-y-3">
          <div v-if="!result && !running"
            class="text-ink-400 text-sm py-12 text-center font-mono">
            Run something to see the output here.
          </div>

          <div v-if="result" class="space-y-3">
            <!-- Stat grid -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
                <p class="eyebrow">exit code</p>
                <p class="font-mono text-lg mt-0.5"
                   :class="result.exit_code === 0 ? 'text-emerald-300' : 'text-rose-300'">
                  {{ result.exit_code }}
                </p>
              </div>
              <div class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
                <p class="eyebrow">duration</p>
                <p class="font-mono text-lg mt-0.5 text-ink-100">{{ result.duration_ms.toFixed(0) }} ms</p>
              </div>
              <div class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
                <p class="eyebrow">timed out</p>
                <p class="font-mono text-lg mt-0.5"
                   :class="result.timed_out ? 'text-rose-300' : 'text-emerald-300'">
                  {{ result.timed_out ? 'yes' : 'no' }}
                </p>
              </div>
              <div class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
                <p class="eyebrow">tests</p>
                <p class="font-mono text-lg mt-0.5 text-ink-100">
                  <span v-if="result.tests_passed != null">
                    <span class="text-emerald-300">{{ result.tests_passed }}</span>
                    <span class="text-ink-500"> / </span>
                    <span class="text-rose-300">{{ result.tests_failed ?? 0 }}</span>
                  </span>
                  <span v-else class="text-ink-400">—</span>
                </p>
              </div>
            </div>

            <!-- Reason -->
            <div class="rounded-lg ring-1 ring-white/5 bg-ink-900/50 px-3 py-2">
              <p class="eyebrow">reason</p>
              <p class="font-mono text-[12px] mt-0.5 text-ink-200">{{ result.short_reason }}</p>
            </div>

            <!-- Stdout -->
            <details open class="rounded-lg ring-1 ring-white/5 bg-ink-950">
              <summary class="px-3 py-2 cursor-pointer font-mono text-[12px] text-ink-300 hover:text-ink-100">
                ◉ stdout ({{ result.stdout.length }} chars)
              </summary>
              <pre class="px-3 py-2 font-mono text-[12px] text-emerald-200 whitespace-pre-wrap overflow-x-auto max-h-64">{{ result.stdout || '(empty)' }}</pre>
            </details>

            <!-- Stderr -->
            <details :open="!!result.stderr" class="rounded-lg ring-1 ring-white/5 bg-ink-950">
              <summary class="px-3 py-2 cursor-pointer font-mono text-[12px] text-ink-300 hover:text-ink-100">
                ◉ stderr ({{ result.stderr.length }} chars)
              </summary>
              <pre class="px-3 py-2 font-mono text-[12px] text-rose-200 whitespace-pre-wrap overflow-x-auto max-h-64">{{ result.stderr || '(empty)' }}</pre>
            </details>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent runs -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Recent sandbox runs</h3>
        <span class="font-mono text-[11px] text-ink-400">last {{ recentRuns.length }} of 20</span>
      </div>
      <div class="panel-body p-0">
        <div v-if="!recentRuns.length" class="text-ink-400 text-sm py-8 text-center font-mono">
          No runs yet.
        </div>
        <table v-else class="w-full text-[12px]">
          <thead class="bg-white/[0.02] text-ink-400 font-mono">
            <tr>
              <th class="px-4 py-2 text-left font-normal">timestamp</th>
              <th class="px-4 py-2 text-left font-normal">lang</th>
              <th class="px-4 py-2 text-left font-normal">backend</th>
              <th class="px-4 py-2 text-left font-normal">status</th>
              <th class="px-4 py-2 text-right font-normal">exit</th>
              <th class="px-4 py-2 text-right font-normal">duration</th>
              <th class="px-4 py-2 text-left font-normal">reason</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in recentRuns" :key="i" class="border-t border-white/5 hover:bg-white/[0.02]">
              <td class="px-4 py-1.5 font-mono text-ink-300">{{ new Date(r.timestamp).toLocaleTimeString() }}</td>
              <td class="px-4 py-1.5 font-mono text-ink-200">{{ r.language }}</td>
              <td class="px-4 py-1.5 font-mono text-ink-300">{{ r.backend }}</td>
              <td class="px-4 py-1.5">
                <span :class="r.success ? 'text-emerald-300' : 'text-rose-300'" class="font-mono">
                  {{ r.success ? '✓ pass' : '✗ fail' }}
                </span>
              </td>
              <td class="px-4 py-1.5 text-right font-mono"
                  :class="r.exit_code === 0 ? 'text-emerald-300' : 'text-rose-300'">
                {{ r.exit_code }}
              </td>
              <td class="px-4 py-1.5 text-right font-mono text-ink-200">{{ r.duration_ms }} ms</td>
              <td class="px-4 py-1.5 font-mono text-ink-400 truncate max-w-md">{{ r.short_reason }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
