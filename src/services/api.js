import axios from 'axios'
import { mockReply } from './mock'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 2500,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const url = error.config?.url || ''
    const method = (error.config?.method || 'get').toLowerCase()
    if (method === 'get') {
      const data = mockReply(url)
      if (data !== null) {
        if (import.meta.env.DEV) console.info('[mock] %s %s', method, url)
        return Promise.resolve({ data, status: 200, statusText: 'OK (mock)', headers: {}, config: error.config })
      }
    }
    return Promise.reject(error)
  }
)

if (USE_MOCK) {
  api.interceptors.request.use((config) => {
    const data = mockReply(config.url || '')
    if (data !== null && (config.method || 'get').toLowerCase() === 'get') {
      config.adapter = () => Promise.resolve({
        data, status: 200, statusText: 'OK (mock)',
        headers: {}, config, request: {},
      })
    }
    return config
  })
}

export default api
