<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAgentsStore } from '@/stores/agents'
import { useBugsStore } from '@/stores/bugs'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const agentsStore = useAgentsStore()
const bugsStore = useBugsStore()
const auth = useAuthStore()

function signOut() {
  auth.logout()
  router.replace({ name: 'Login' })
}

const navItems = [
  { path: '/',                label: 'Overview',         icon: 'overview' },
  { path: '/consensus',       label: 'Consensus',        icon: 'consensus' },
  { path: '/consensus-lab',   label: 'Consensus Lab',    icon: 'flask' },
  { path: '/bugs',            label: 'Bug Stream',       icon: 'bug' },
  { path: '/fixes',           label: 'Fix History',      icon: 'wrench' },
  { path: '/agents',          label: 'Agent Mesh',       icon: 'cpu' },
  { path: '/sandbox',         label: 'Sandbox',          icon: 'sandbox' },
  { path: '/evaluation',      label: 'Evaluation',       icon: 'chart' },
]

const researchItems = [
  { path: '/timeline',       label: 'Timeline',        icon: 'timeline' },
  { path: '/heatmap',        label: 'Agent Heatmap',    icon: 'grid' },
  { path: '/byzantine-lab',  label: 'Byzantine Lab',    icon: 'zap' },
  { path: '/knowledge-graph',label: 'Knowledge Graph',  icon: 'graph' },
  { path: '/diff-theater',   label: 'Diff Theater',     icon: 'diff' },
]

const isActive = (path) => path === '/' ? route.path === '/' : route.path.startsWith(path)
</script>

<template>
  <aside class="w-64 fixed inset-y-0 left-0 z-30 flex flex-col border-r border-white/5 bg-ink-900/80 backdrop-blur-xl">
    <!-- Brand -->
    <div class="px-5 py-5 border-b border-white/5">
      <div class="flex items-center gap-3">
        <div class="relative w-10 h-10 rounded-xl bg-ink-950 ring-1 ring-white/10 flex items-center justify-center overflow-hidden">
          <svg class="w-7 h-7" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="18" stroke="url(#sb-g)" stroke-width="2.5"/>
            <circle cx="32" cy="14" r="3" fill="#A855F7"/>
            <circle cx="50" cy="42" r="3" fill="#22D3EE"/>
            <circle cx="14" cy="42" r="3" fill="#34D399"/>
            <defs><linearGradient id="sb-g" x1="0" x2="64" y1="0" y2="64">
              <stop offset="0" stop-color="#A855F7"/><stop offset=".5" stop-color="#7C8CFF"/><stop offset="1" stop-color="#22D3EE"/>
            </linearGradient></defs>
          </svg>
        </div>
        <div class="leading-tight">
          <p class="font-display text-[15px] font-semibold tracking-tight text-ink-100">CodeFlow AI</p>
          <p class="text-[10px] font-mono uppercase tracking-[0.18em] text-ink-400">BFT · MARP</p>
        </div>
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
      <p class="px-3 mb-2 eyebrow">Operations</p>
      <router-link
        v-for="item in navItems" :key="item.path" :to="item.path"
        :class="['group flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] font-medium transition relative',
          isActive(item.path)
            ? 'text-ink-100 bg-white/[0.04] ring-1 ring-white/10'
            : 'text-ink-400 hover:text-ink-100 hover:bg-white/[0.02]']">
        <span v-if="isActive(item.path)" class="absolute left-0 top-2 bottom-2 w-[2px] rounded-full bg-gradient-to-b from-violet-400 via-brand-400 to-cyan-400"></span>

        <!-- icons -->
        <svg v-if="item.icon==='overview'"  class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>
        <svg v-if="item.icon==='consensus'" class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="M12 8v3m-5 5 4-3m6 3-4-3"/></svg>
        <svg v-if="item.icon==='bug'"       class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="7" width="10" height="13" rx="5"/><path d="M12 7V4m-3 6H5m14 0h-4M9 14H5m14 0h-4M9 18l-3 2m9-2 3 2"/></svg>
        <svg v-if="item.icon==='wrench'"    class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 0 0 5 5L21 12l-9 9-3-3 9-9-1.7-1.7Z"/></svg>
        <svg v-if="item.icon==='cpu'"       class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 2v3m6-3v3M9 19v3m6-3v3M2 9h3m-3 6h3m14-6h3m-3 6h3"/></svg>
        <svg v-if="item.icon==='chart'"     class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-7"/></svg>
        <svg v-if="item.icon==='sandbox'"   class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M10 9l5 3-5 3v-6Z"/></svg>
        <svg v-if="item.icon==='flask'"     class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6"/><path d="M10 3v6L4 19a2 2 0 0 0 1.7 3h12.6A2 2 0 0 0 20 19l-6-10V3"/><path d="M7 14h10"/></svg>

        <span class="flex-1">{{ item.label }}</span>
        <span v-if="item.icon==='bug' && bugsStore.activeBugs.length"
          class="font-mono text-[10px] px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-300 ring-1 ring-rose-500/30">
          {{ bugsStore.activeBugs.length }}
        </span>
      </router-link>

      <p class="px-3 mt-4 mb-2 eyebrow">Research</p>
      <router-link
        v-for="item in researchItems" :key="item.path" :to="item.path"
        :class="['group flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] font-medium transition relative',
          isActive(item.path)
            ? 'text-ink-100 bg-white/[0.04] ring-1 ring-white/10'
            : 'text-ink-400 hover:text-ink-100 hover:bg-white/[0.02]']">
        <span v-if="isActive(item.path)" class="absolute left-0 top-2 bottom-2 w-[2px] rounded-full bg-gradient-to-b from-violet-400 via-brand-400 to-cyan-400"></span>

        <!-- Research icons -->
        <svg v-if="item.icon==='timeline'" class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18"/><circle cx="6" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="18" cy="12" r="2"/><path d="M6 8v-2m12 6v2"/></svg>
        <svg v-if="item.icon==='grid'"     class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="5" height="5" rx="1"/><rect x="10" y="3" width="5" height="5" rx="1"/><rect x="17" y="3" width="5" height="5" rx="1"/><rect x="3" y="10" width="5" height="5" rx="1"/><rect x="10" y="10" width="5" height="5" rx="1"/><rect x="17" y="10" width="5" height="5" rx="1"/><rect x="3" y="17" width="5" height="5" rx="1"/><rect x="10" y="17" width="5" height="5" rx="1"/><rect x="17" y="17" width="5" height="5" rx="1"/></svg>
        <svg v-if="item.icon==='zap'"      class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8Z"/></svg>
        <svg v-if="item.icon==='graph'"    class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="8" r="2.5"/><circle cx="8" cy="18" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 7.5 16 9m-8 8 8-7m0 0v8"/></svg>
        <svg v-if="item.icon==='diff'"     class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 3v18"/><path d="M7 8h2m-2 4h3m8-4h-2m2 4h-3"/></svg>

        <span class="flex-1">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Footer status -->
    <div class="p-3 border-t border-white/5 space-y-2">
      <div class="rounded-xl border border-white/5 bg-ink-850/60 p-3 space-y-2">
        <div class="flex items-center justify-between">
          <span class="eyebrow">Mesh</span>
          <span class="font-mono text-[10px] text-ink-300">
            {{ agentsStore.onlineAgents.length }}/{{ agentsStore.agents.length || 9 }}
          </span>
        </div>
        <div class="bar-track">
          <div class="bar-fill bg-gradient-to-r from-violet-400 via-brand-400 to-cyan-400"
               :style="{ width: ((agentsStore.onlineAgents.length / Math.max(1, agentsStore.agents.length || 9)) * 100) + '%' }"></div>
        </div>
        <div class="flex items-center justify-between text-[11px]">
          <div class="flex items-center gap-1.5">
            <span :class="agentsStore.isConsensusReady ? 'dot dot-online' : 'dot dot-offline'"></span>
            <span :class="agentsStore.isConsensusReady ? 'text-emerald-300' : 'text-ink-400'">
              {{ agentsStore.isConsensusReady ? 'Quorum ready' : 'Quorum forming' }}
            </span>
          </div>
          <span class="kbd">PBFT</span>
        </div>
      </div>
      <div v-if="auth.user" class="flex items-center gap-2 px-2 pt-1">
        <div class="w-7 h-7 rounded-full bg-gradient-to-br from-violet-400 via-brand-400 to-cyan-400 flex items-center justify-center text-[11px] font-mono font-bold text-white">
          {{ auth.user.username.charAt(0).toUpperCase() }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-[12px] text-ink-100 truncate">{{ auth.user.username }}</p>
          <p class="font-mono text-[9px] uppercase tracking-wider text-ink-400">{{ auth.user.role }}</p>
        </div>
        <button type="button" @click="signOut"
                title="Sign out" aria-label="Sign out"
                class="p-1.5 rounded-md text-ink-400 hover:text-rose-300 hover:bg-rose-500/10 transition">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/>
          </svg>
        </button>
      </div>
      <p class="px-2 text-[10px] font-mono text-ink-400 leading-snug">
        Millicent Mufambi · H240624A<br/>Harare Institute of Technology
      </p>
    </div>
  </aside>
</template>
