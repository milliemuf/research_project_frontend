/**
 * CodeFlow AI - Frontend Entry Point
 *
 * Byzantine Fault-Tolerant Multi-Agent System for Autonomous Runtime Program Repair
 *
 * Author: Millicent Mufambi (H240624A)
 * Institution: Harare Institute of Technology
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/theme'
import './assets/main.css'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)

// Initialize theme before mount so the correct palette is painted on first frame.
useThemeStore(pinia).init()

app.mount('#app')
