<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useWebSocket } from '@/services/websocket'
import { useThemeStore } from '@/stores/theme'

const route = useRoute()
const { connected } = useWebSocket()
const theme = useThemeStore()
const pageTitle = computed(() => route.meta?.title || 'Overview')

const clock = ref('')
let timer
function tick() {
  const d = new Date()
  clock.value = d.toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
}
onMounted(() => { tick(); timer = setInterval(tick, 1000) })
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <header class="h-14 sticky top-0 z-20 flex items-center justify-between px-6 border-b border-white/5 bg-ink-950/70 backdrop-blur-xl">
    <div class="flex items-center gap-3">
      <span class="eyebrow">CodeFlow / </span>
      <h2 class="font-display text-[15px] font-semibold text-ink-100 tracking-tight">{{ pageTitle }}</h2>
    </div>

    <div class="flex items-center gap-3">
      <span class="hidden md:inline font-mono text-[11px] text-ink-400">{{ clock }}</span>
      <span class="hidden md:inline kbd">v0.1.0</span>

      <!-- Theme toggle -->
      <button
        type="button"
        @click="theme.toggle()"
        :title="theme.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        :aria-label="theme.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        class="relative inline-flex items-center h-7 w-12 rounded-full border border-white/10 bg-ink-800/70 transition hover:bg-ink-700/70 focus:outline-none focus:ring-2 focus:ring-brand-500/40">
        <span class="absolute left-1 top-1 w-5 h-5 rounded-full bg-gradient-to-br from-violet-400 via-brand-400 to-cyan-400 shadow transition-transform duration-200"
              :style="{ transform: theme.isLight ? 'translateX(20px)' : 'translateX(0)' }"></span>
        <svg class="absolute left-1.5 top-1.5 w-4 h-4 text-ink-300 transition-opacity"
             :class="theme.isDark ? 'opacity-0' : 'opacity-100'"
             viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>
        </svg>
        <svg class="absolute right-1.5 top-1.5 w-4 h-4 text-ink-300 transition-opacity"
             :class="theme.isDark ? 'opacity-100' : 'opacity-0'"
             viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>
        </svg>
      </button>

      <div class="flex items-center gap-2 px-2.5 py-1 rounded-full border"
           :class="connected ? 'border-emerald-500/30 bg-emerald-500/10' : 'border-rose-500/30 bg-rose-500/10'">
        <span v-if="connected" class="live-dot"></span>
        <span v-else class="dot dot-offline"></span>
        <span class="font-mono text-[10px] uppercase tracking-wider"
              :class="connected ? 'text-emerald-300' : 'text-rose-300'">
          {{ connected ? 'Live · WS' : 'Mock · No WS' }}
        </span>
      </div>
    </div>
  </header>
</template>
