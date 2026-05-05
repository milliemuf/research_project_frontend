<script setup>
defineProps({
  title: String,
  value: [String, Number],
  subtitle: String,
  trend: String,
  trendUp: Boolean,
  icon: String,
  color: {
    type: String,
    default: 'blue'
  }
})
</script>

<template>
  <div class="card">
    <div class="card-body">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-400">{{ title }}</p>
          <p class="text-2xl font-bold text-white mt-1">{{ value }}</p>
          <p v-if="subtitle" class="text-xs text-gray-500 mt-1">{{ subtitle }}</p>
        </div>
        <div
          class="w-12 h-12 rounded-lg flex items-center justify-center"
          :class="`bg-${color}-500/20`"
        >
          <svg v-if="icon === 'bug'" class="w-6 h-6" :class="`text-${color}-400`" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-if="icon === 'check'" class="w-6 h-6" :class="`text-${color}-400`" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-if="icon === 'agent'" class="w-6 h-6" :class="`text-${color}-400`" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <svg v-if="icon === 'time'" class="w-6 h-6" :class="`text-${color}-400`" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
      <div v-if="trend" class="mt-3 flex items-center text-sm">
        <span
          :class="trendUp ? 'text-green-400' : 'text-red-400'"
        >
          {{ trendUp ? '↑' : '↓' }} {{ trend }}
        </span>
        <span class="text-gray-500 ml-2">vs last hour</span>
      </div>
    </div>
  </div>
</template>
