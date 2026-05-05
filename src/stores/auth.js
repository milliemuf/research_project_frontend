import { defineStore } from 'pinia'

const TOKEN_KEY = 'codeflow.token'
const USER_KEY = 'codeflow.user'

function readUser() {
  try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null') } catch { return null }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || null,
    user: readUser(),
  }),
  getters: {
    isAuthenticated: (s) => Boolean(s.token),
  },
  actions: {
    // Mock login: accept any non-empty username/password, mint a local token.
    // No backend hit — we'll replace this with a real /auth/login call later.
    async login({ username, password }) {
      await new Promise(r => setTimeout(r, 350))
      if (!username?.trim() || !password?.trim()) {
        throw new Error('Username and password are required')
      }
      const token = 'mock.' + btoa(`${username}:${Date.now()}`)
      const user = { username: username.trim(), role: 'researcher' }
      this.token = token
      this.user = user
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },
  },
})
