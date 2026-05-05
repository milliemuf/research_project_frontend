<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useWebSocket } from '@/services/websocket'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'
import Header from '@/components/Header.vue'

const route = useRoute()
const auth = useAuthStore()
const { connect, disconnect } = useWebSocket()

const isAppLayout = computed(() => auth.isAuthenticated && route.meta?.layout !== 'blank')

// Only open the WebSocket when the user is inside the app shell — the login
// screen doesn't need a live feed, and opening a doomed socket wastes reconnect
// cycles that delay first paint.
watch(isAppLayout, (on) => {
  if (on) connect()
  else disconnect()
}, { immediate: true })
</script>

<template>
  <div v-if="isAppLayout" class="min-h-screen flex bg-ink-950 text-ink-100">
    <Sidebar />
    <div class="flex-1 flex flex-col ml-64 min-w-0">
      <Header />
      <main class="flex-1 overflow-auto relative">
        <div class="absolute inset-0 bg-grid opacity-[0.4] pointer-events-none [mask-image:radial-gradient(60%_60%_at_50%_0%,#000_30%,transparent_80%)]"></div>
        <div class="relative p-6 md:p-8">
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
  </div>

  <router-view v-else />
</template>

<style>
.page-enter-active { animation: pgUp .35s cubic-bezier(.2,.8,.2,1) both; }
.page-leave-active { animation: pgOut .15s ease-in both; }
@keyframes pgUp  { from { opacity:0; transform: translateY(10px); } to { opacity:1; transform: none; } }
@keyframes pgOut { from { opacity:1; } to { opacity:0; } }
</style>
