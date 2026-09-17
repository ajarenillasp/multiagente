<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Progress principal -->
    <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
      <h2 class="text-2xl font-bold text-white mb-6">Ejecución en Progreso</h2>
      
      <div class="mb-8">
        <div class="flex justify-between text-sm text-blue-200 mb-2">
          <span>Progreso general</span>
          <span>{{ progress }}%</span>
        </div>
        <div class="h-4 bg-white/20 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-500 ease-out"
            :style="{ width: progress + '%' }"
          ></div>
        </div>
      </div>

      <!-- Estado de agentes -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <div 
          v-for="(agent, index) in agents" 
          :key="index"
          class="bg-white/10 rounded-xl p-4 border border-white/20"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold text-white">{{ agent.role }}</h3>
            <span 
              class="status-badge px-2 py-1 rounded-full text-xs"
              :class="getAgentStatusClass(agent)"
            >
              {{ getAgentStatus(agent) }}
            </span>
          </div>
          <p class="text-xs text-blue-200">{{ agent.task }}</p>
          
          <!-- Barra de progreso individual -->
          <div class="mt-3 h-2 bg-white/20 rounded-full overflow-hidden">
            <div 
              class="h-full bg-blue-400 transition-all duration-300"
              :style="{ width: getAgentProgress(agent) + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Iteraciones de verificación -->
      <div class="bg-white/10 rounded-xl p-6 border border-white/20">
        <h3 class="text-lg font-semibold text-white mb-4">Iteraciones de Verificación</h3>
        <div class="space-y-3">
          <div 
            v-for="n in 5" 
            :key="n"
            class="flex items-center justify-between p-3 bg-white/10 rounded-lg"
          >
            <div class="flex items-center gap-3">
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center"
                :class="getIterationClass(n)"
              >
                <span v-if="getIterationClass(n).includes('green')" class="text-white text-sm">✓</span>
                <span v-else-if="getIterationClass(n).includes('blue')" class="text-white text-sm">{{ n }}</span>
                <span v-else class="text-blue-200 text-sm">{{ n }}</span>
              </div>
              <span class="text-white">Iteración {{ n }}</span>
            </div>
            <span 
              class="text-sm"
              :class="getIterationTextClass(n)"
            >
              {{ getIterationText(n) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExecutionMonitor',
  props: {
    agents: {
      type: Array,
      required: true
    },
    progress: {
      type: Number,
      default: 0
    }
  },
  methods: {
    getAgentStatus(agent) {
      if (this.progress < 20) return 'Pendiente';
      if (this.progress < 40) return 'Analizando';
      if (this.progress < 60) return 'Investigando';
      if (this.progress < 80) return 'Desarrollando';
      if (this.progress < 95) return 'Verificando';
      return 'Completado';
    },
    getAgentStatusClass(agent) {
      const status = this.getAgentStatus(agent);
      if (status === 'Pendiente') return 'bg-slate-500/30 text-slate-200';
      if (status === 'Analizando' || status === 'Investigando' || status === 'Desarrollando') 
        return 'bg-blue-500/30 text-blue-200 animate-pulse';
      if (status === 'Verificando') return 'bg-amber-500/30 text-amber-200';
      return 'bg-green-500/30 text-green-200';
    },
    getAgentProgress(agent) {
      if (this.progress < 20) return 0;
      if (this.progress >= 95) return 100;
      // Progreso escalonado por fase
      const baseProgress = ((this.progress - 20) / 75) * 100;
      return Math.min(100, Math.max(0, baseProgress));
    },
    getIterationClass(n) {
      const thresholds = [40, 55, 70, 85, 95];
      if (this.progress >= thresholds[n - 1]) return 'bg-green-500';
      if (this.progress >= thresholds[n - 1] - 15) return 'bg-blue-500';
      return 'bg-white/20';
    },
    getIterationText(n) {
      const thresholds = [40, 55, 70, 85, 95];
      if (this.progress >= thresholds[n - 1]) return 'Completada';
      if (this.progress >= thresholds[n - 1] - 15) return 'En progreso...';
      return 'Pendiente';
    },
    getIterationTextClass(n) {
      const thresholds = [40, 55, 70, 85, 95];
      if (this.progress >= thresholds[n - 1]) return 'text-green-300';
      if (this.progress >= thresholds[n - 1] - 15) return 'text-blue-300';
      return 'text-slate-400';
    }
  }
};
</script>
