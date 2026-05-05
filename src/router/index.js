import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'Sign in', public: true, layout: 'blank' }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Dashboard' }
  },
  {
    path: '/bugs',
    name: 'Bugs',
    component: () => import('@/views/BugList.vue'),
    meta: { title: 'Bugs' }
  },
  {
    path: '/bugs/:id',
    name: 'BugDetail',
    component: () => import('@/views/BugDetail.vue'),
    meta: { title: 'Bug Details' }
  },
  {
    path: '/fixes',
    name: 'Fixes',
    component: () => import('@/views/FixHistory.vue'),
    meta: { title: 'Fix History' }
  },
  {
    path: '/agents',
    name: 'Agents',
    component: () => import('@/views/AgentStatus.vue'),
    meta: { title: 'Agent Status' }
  },
  {
    path: '/consensus',
    name: 'Consensus',
    component: () => import('@/views/ConsensusView.vue'),
    meta: { title: 'Consensus Monitor' }
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: () => import('@/views/Evaluation.vue'),
    meta: { title: 'Evaluation' }
  },
  {
    path: '/timeline/:bugId?',
    name: 'RepairTimeline',
    component: () => import('@/views/RepairTimeline.vue'),
    meta: { title: 'Repair Timeline' }
  },
  {
    path: '/heatmap',
    name: 'AgentHeatmap',
    component: () => import('@/views/AgentHeatmap.vue'),
    meta: { title: 'Agent Heatmap' }
  },
  {
    path: '/byzantine-lab',
    name: 'ByzantineLab',
    component: () => import('@/views/ByzantineLab.vue'),
    meta: { title: 'Byzantine Lab' }
  },
  {
    path: '/knowledge-graph',
    name: 'KnowledgeGraph',
    component: () => import('@/views/KnowledgeGraph.vue'),
    meta: { title: 'Knowledge Graph' }
  },
  {
    path: '/diff-theater/:bugId?',
    name: 'DiffTheater',
    component: () => import('@/views/DiffTheater.vue'),
    meta: { title: 'Diff Theater' }
  },
  {
    path: '/sandbox',
    name: 'Sandbox',
    component: () => import('@/views/Sandbox.vue'),
    meta: { title: 'Sandbox' }
  },
  {
    path: '/consensus-lab',
    name: 'ConsensusLab',
    component: () => import('@/views/ConsensusLab.vue'),
    meta: { title: 'Consensus Lab' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'CodeFlow'} | CodeFlow AI`
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return next({ name: 'Login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : {} })
  }
  if (to.name === 'Login' && auth.isAuthenticated) {
    return next({ path: '/' })
  }
  next()
})

export default router
