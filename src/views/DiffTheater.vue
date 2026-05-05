<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBugsStore } from '@/stores/bugs'
import api from '@/services/api'

const route = useRoute()
const bugsStore = useBugsStore()
const data = ref(null)
const activeIdx = ref(0)

onMounted(async () => {
  await bugsStore.fetchBugs().catch(() => {})
  const bugId = route.params.bugId || bugsStore.bugs[0]?.id || 'bug-0001'
  try {
    const res = await api.get(`/api/v1/diff-theater/${bugId}`)
    data.value = res.data
    // Default to accepted proposal
    const accIdx = res.data.proposals.findIndex(p => p.verdict === 'accepted')
    if (accIdx >= 0) activeIdx.value = accIdx
  } catch (e) { console.warn('diff-theater:', e.message) }
})

const activeProposal = computed(() => data.value?.proposals[activeIdx.value] || null)

function isFaultLine(i) { return data.value?.fault_lines?.includes(i) }
function isModifiedLine(i) {
  if (!activeProposal.value || !data.value) return false
  return data.value.original_lines[i] !== activeProposal.value.modified_lines[i]
}

function agentBg(type) {
  return type === 'healer' ? 'bg-agent-healer'
       : type === 'validator' ? 'bg-agent-validator'
       : 'bg-agent-analyzer'
}
</script>

<template>
  <div v-if="data" class="space-y-4">
    <!-- Header -->
    <section class="panel px-5 py-3 flex flex-wrap items-center gap-4 justify-between">
      <div>
        <p class="eyebrow">Code repair comparison</p>
        <h2 class="font-display text-lg text-ink-100">Diff Theater · {{ data.bug.id }}</h2>
      </div>
      <div class="flex items-center gap-2">
        <span :class="`sev-${data.bug.severity}`">{{ data.bug.severity }}</span>
        <span :class="`status status-${data.bug.status}`">{{ data.bug.status.replace('_',' ') }}</span>
        <span class="font-mono text-[11px] text-ink-400">{{ data.file_path }}</span>
      </div>
    </section>

    <!-- Proposal tabs -->
    <section class="flex flex-wrap gap-2">
      <button v-for="(p, i) in data.proposals" :key="i"
        @click="activeIdx = i"
        :class="['btn gap-3', activeIdx === i ? 'btn-primary' : 'btn-ghost']">
        <div :class="['w-5 h-5 rounded flex items-center justify-center text-[9px] font-mono font-bold text-white', agentBg(p.agent.agent_type)]">
          H
        </div>
        <span>{{ p.agent.llm_provider }}</span>
        <span :class="p.verdict === 'accepted'
          ? 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30'
          : 'bg-rose-500/15 text-rose-300 ring-1 ring-rose-500/30'"
          class="text-[9px] px-1.5 py-0.5 rounded font-mono uppercase">
          {{ p.verdict }}
        </span>
      </button>
    </section>

    <!-- Split pane -->
    <section class="grid grid-cols-1 xl:grid-cols-2 gap-px bg-white/5 rounded-2xl overflow-hidden">
      <!-- Original code -->
      <div class="panel rounded-none xl:rounded-l-2xl xl:rounded-r-none">
        <div class="panel-header">
          <h3 class="panel-title">Original</h3>
          <span class="tag tag-rose">Fault</span>
        </div>
        <div class="p-0">
          <div class="code-block rounded-none border-0">
            <pre class="m-0 p-0"><div v-for="(line, i) in data.original_lines" :key="'o'+i"
  :class="['diff-row', isFaultLine(i) ? 'diff-del' : 'diff-ctx']"><span class="line-num">{{ i + 1 }}</span>{{ line }}</div></pre>
          </div>
        </div>
      </div>

      <!-- Proposed diff -->
      <div class="panel rounded-none xl:rounded-r-2xl xl:rounded-l-none">
        <div class="panel-header">
          <h3 class="panel-title">{{ activeProposal?.agent?.name || 'Proposed' }}</h3>
          <span v-if="activeProposal" class="font-mono text-[10px] text-ink-400">
            confidence {{ ((activeProposal.confidence || 0) * 100).toFixed(0) }}%
          </span>
        </div>
        <div class="p-0">
          <div class="code-block rounded-none border-0">
            <pre v-if="activeProposal" class="m-0 p-0"><div v-for="(line, i) in activeProposal.modified_lines" :key="'m'+i"
  :class="['diff-row', isModifiedLine(i) ? 'diff-add' : 'diff-ctx']"><span class="line-num">{{ i + 1 }}</span>{{ line }}</div></pre>
          </div>
        </div>
      </div>
    </section>

    <!-- Validator verdicts -->
    <section v-if="activeProposal" class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Validator verdicts</h3>
        <span class="font-mono text-[10px] text-ink-400">
          {{ activeProposal.validator_votes.filter(v => v.vote === 'approve').length }}/{{ activeProposal.validator_votes.length }} approved
        </span>
      </div>
      <div class="panel-body grid grid-cols-1 md:grid-cols-3 gap-3">
        <div v-for="v in activeProposal.validator_votes" :key="v.agent_id"
          class="panel-quiet p-3 space-y-1.5 ring-validator">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-6 h-6 rounded-md bg-agent-validator flex items-center justify-center text-[10px] font-mono font-bold text-white">V</div>
              <span class="font-mono text-[10px] text-ink-300">{{ v.agent_id }}</span>
            </div>
            <span :class="v.vote === 'approve' ? 'status status-resolved' : 'status status-failed'" class="!text-[9px]">
              {{ v.vote }}
            </span>
          </div>
          <p class="font-mono text-[10.5px] text-ink-400 leading-snug">{{ v.reason }}</p>
        </div>
      </div>
    </section>
  </div>
</template>
