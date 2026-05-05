<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const remember = ref(true)
const submitting = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.login({ username: username.value, password: password.value })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.replace(redirect)
  } catch (e) {
    error.value = e?.message || 'Sign-in failed'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-ink-950 text-ink-100 relative overflow-hidden">
    <div class="absolute inset-0 bg-grid opacity-[0.35] pointer-events-none
                [mask-image:radial-gradient(60%_60%_at_50%_40%,#000_30%,transparent_80%)]"></div>
    <div class="absolute inset-0 pointer-events-none"
         style="background-image: var(--page-glow);"></div>

    <div class="relative w-full max-w-md px-5">
      <!-- Brand mark -->
      <div class="flex items-center gap-3 mb-6 justify-center">
        <div class="w-10 h-10 rounded-xl bg-ink-900 ring-1 ring-white/10 flex items-center justify-center">
          <svg class="w-7 h-7" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="18" stroke="url(#lg-g)" stroke-width="2.5"/>
            <circle cx="32" cy="14" r="3" fill="#A855F7"/>
            <circle cx="50" cy="42" r="3" fill="#22D3EE"/>
            <circle cx="14" cy="42" r="3" fill="#34D399"/>
            <defs><linearGradient id="lg-g" x1="0" x2="64" y1="0" y2="64">
              <stop offset="0" stop-color="#A855F7"/><stop offset=".5" stop-color="#7C8CFF"/><stop offset="1" stop-color="#22D3EE"/>
            </linearGradient></defs>
          </svg>
        </div>
        <div class="leading-tight">
          <p class="font-display text-lg font-semibold tracking-tight text-ink-100">CodeFlow AI</p>
          <p class="text-[10px] font-mono uppercase tracking-[0.22em] text-ink-400">BFT · Multi-Agent Repair</p>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h1 class="panel-title">Sign in</h1>
          <span class="kbd">mock</span>
        </div>
        <form @submit.prevent="submit" class="panel-body space-y-4">
          <div>
            <label class="block eyebrow mb-1.5" for="u">Username</label>
            <input id="u" v-model="username" type="text" autocomplete="username"
                   placeholder="admin"
                   class="w-full rounded-xl bg-ink-850/60 border border-white/10 px-3.5 py-2.5 text-sm text-ink-100 placeholder:text-ink-500 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500/40 transition"/>
          </div>
          <div>
            <label class="block eyebrow mb-1.5" for="p">Password</label>
            <input id="p" v-model="password" type="password" autocomplete="current-password"
                   placeholder="••••••••"
                   class="w-full rounded-xl bg-ink-850/60 border border-white/10 px-3.5 py-2.5 text-sm text-ink-100 placeholder:text-ink-500 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500/40 transition"/>
          </div>

          <div class="flex items-center justify-between text-[12px]">
            <label class="flex items-center gap-2 text-ink-300 cursor-pointer select-none">
              <input v-model="remember" type="checkbox" class="accent-brand-500 w-3.5 h-3.5"/>
              Remember me
            </label>
            <span class="font-mono text-[10px] text-ink-400">any credentials work</span>
          </div>

          <div v-if="error" class="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-[12px] text-rose-300">
            {{ error }}
          </div>

          <button type="submit" :disabled="submitting"
                  class="btn btn-primary w-full justify-center disabled:opacity-60 disabled:cursor-not-allowed">
            <span v-if="!submitting">Enter console →</span>
            <span v-else class="inline-flex items-center gap-2">
              <span class="w-3 h-3 rounded-full border-2 border-white/40 border-t-white animate-spin"></span>
              Authenticating
            </span>
          </button>
        </form>
      </div>

      <p class="text-center mt-5 font-mono text-[10px] text-ink-400">
        Millicent Mufambi · H240624A · Harare Institute of Technology
      </p>
    </div>
  </div>
</template>
