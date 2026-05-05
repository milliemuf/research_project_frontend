import { defineStore } from 'pinia'

const STORAGE_KEY = 'codeflow.theme'

function resolveInitial() {
  const saved = typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null
  if (saved === 'light' || saved === 'dark') return saved
  if (typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: light)').matches) return 'light'
  return 'dark'
}

function applyTheme(mode) {
  const root = document.documentElement
  root.classList.toggle('dark', mode === 'dark')
  root.classList.toggle('light', mode === 'light')
}

export const useThemeStore = defineStore('theme', {
  state: () => ({ mode: 'dark' }),
  getters: {
    isDark: (s) => s.mode === 'dark',
    isLight: (s) => s.mode === 'light',
  },
  actions: {
    init() {
      this.mode = resolveInitial()
      applyTheme(this.mode)
    },
    set(mode) {
      this.mode = mode === 'light' ? 'light' : 'dark'
      localStorage.setItem(STORAGE_KEY, this.mode)
      applyTheme(this.mode)
    },
    toggle() {
      this.set(this.mode === 'dark' ? 'light' : 'dark')
    },
  },
})
