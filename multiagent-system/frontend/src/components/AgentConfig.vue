<template>
  <div class="space-y-6 animate-fade-in">
    <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
      <h2 class="text-2xl font-bold text-white mb-4">Configuración de Agentes Propuesta</h2>
      <p class="text-blue-200 mb-6">
        El agente arquitecto ha diseñado el siguiente equipo para tu proyecto:
      </p>

      <!-- Grid de agentes -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <div 
          v-for="(agent, index) in agents" 
          :key="index"
          class="bg-white/10 rounded-xl p-5 border border-white/20 hover:border-blue-400 transition-colors"
        >
          <div class="flex items-start justify-between mb-3">
            <h3 class="text-lg font-semibold text-white">{{ agent.role }}</h3>
            <span class="px-2 py-1 bg-blue-500/30 rounded-full text-xs text-blue-200">
              Agente {{ index + 1 }}
            </span>
          </div>
          
          <div class="space-y-2 text-sm">
            <div>
              <span class="text-blue-300">Tarea:</span>
              <p class="text-white mt-1">{{ agent.task }}</p>
            </div>
            
            <div>
              <span class="text-blue-300">Modelo:</span>
              <select 
                v-model="agent.model"
                class="mt-1 w-full bg-white/20 border border-white/30 rounded px-2 py-1 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="llama3:70b">Llama3 70B (Análisis)</option>
                <option value="codellama:34b">CodeLlama 34B (Código)</option>
                <option value="mistral:7b">Mistral 7B (Rápido)</option>
                <option value="mixtral:8x7b">Mixtral 8x7B (Balanceado)</option>
              </select>
            </div>
            
            <div>
              <span class="text-blue-300">Herramientas:</span>
              <div class="flex flex-wrap gap-1 mt-1">
                <span 
                  v-for="tool in agent.tools" 
                  :key="tool"
                  class="px-2 py-0.5 bg-white/20 rounded text-xs text-white"
                >
                  {{ tool }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflow visual -->
      <div class="bg-white/10 rounded-xl p-6 border border-white/20 mb-6">
        <h3 class="text-lg font-semibold text-white mb-4">Workflow de Ejecución</h3>
        <div class="flex flex-wrap items-center justify-center gap-3">
          <div class="flex flex-col items-center">
            <div class="w-16 h-16 rounded-full bg-blue-500/30 border-2 border-blue-400 flex items-center justify-center text-white font-bold">
              1
            </div>
            <span class="text-xs text-blue-200 mt-2">Análisis</span>
          </div>
          
          <svg class="w-6 h-6 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
          
          <div class="flex flex-col items-center">
            <div class="w-16 h-16 rounded-full bg-indigo-500/30 border-2 border-indigo-400 flex items-center justify-center text-white font-bold">
              2
            </div>
            <span class="text-xs text-blue-200 mt-2">Búsqueda</span>
          </div>
          
          <svg class="w-6 h-6 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
          
          <div class="flex flex-col items-center">
            <div class="w-16 h-16 rounded-full bg-purple-500/30 border-2 border-purple-400 flex items-center justify-center text-white font-bold">
              3
            </div>
            <span class="text-xs text-blue-200 mt-2">Desarrollo</span>
          </div>
          
          <svg class="w-6 h-6 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
          
          <div class="flex flex-col items-center">
            <div class="w-16 h-16 rounded-full bg-amber-500/30 border-2 border-amber-400 flex items-center justify-center text-white font-bold">
              4
            </div>
            <span class="text-xs text-blue-200 mt-2">Verificación ×5</span>
          </div>
          
          <svg class="w-6 h-6 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
          
          <div class="flex flex-col items-center">
            <div class="w-16 h-16 rounded-full bg-green-500/30 border-2 border-green-400 flex items-center justify-center text-white font-bold">
              5
            </div>
            <span class="text-xs text-blue-200 mt-2">Edición</span>
          </div>
        </div>
      </div>

      <!-- Resumen de configuración -->
      <div class="bg-white/10 rounded-xl p-4 border border-white/20 mb-6">
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <p class="text-2xl font-bold text-white">{{ agents.length }}</p>
            <p class="text-xs text-blue-300">Agentes</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-white">5</p>
            <p class="text-xs text-blue-300">Iteraciones</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-white">~15-30min</p>
            <p class="text-xs text-blue-300">Tiempo est.</p>
          </div>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="flex justify-center gap-4">
        <button 
          @click="$emit('modify')"
          class="px-6 py-3 bg-white/20 text-white font-semibold rounded-lg hover:bg-white/30 transition-colors"
        >
          Modificar Configuración
        </button>
        <button 
          @click="$emit('approve', { agents })"
          class="px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl"
        >
          <span class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            Aprobar y Ejecutar
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AgentConfig',
  props: {
    projectData: {
      type: Object,
      required: true
    }
  },
  emits: ['approve', 'modify'],
  data() {
    return {
      agents: [
        {
          role: 'Arquitecto',
          task: 'Analizar requisitos y diseñar estructura del equipo',
          model: 'llama3:70b',
          tools: ['Análisis', 'Planificación']
        },
        {
          role: 'Investigador',
          task: 'Búsqueda exhaustiva de información y referencias',
          model: 'mistral:7b',
          tools: ['Búsqueda Web', 'Validación']
        },
        {
          role: 'Especialista en Dominio',
          task: 'Desarrollo de contenido técnico especializado',
          model: 'llama3:70b',
          tools: ['Análisis', 'Síntesis']
        },
        {
          role: 'Verificador',
          task: 'Validación en 5 iteraciones para detectar alucinaciones',
          model: 'mixtral:8x7b',
          tools: ['Validación', 'Fact-checking']
        },
        {
          role: 'Editor',
          task: 'Formateo final y verificación de sintaxis',
          model: 'codellama:34b',
          tools: ['Formato', 'Sintaxis']
        }
      ]
    };
  }
};
</script>
