<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
    <!-- Header -->
    <header class="bg-white/10 backdrop-blur-md border-b border-white/20">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-white">
          🤖 Multi-Agent System - Jetson Thor
        </h1>
        <p class="text-blue-200 mt-2">
          Generación de propuestas europeas y código con calidad extrema
        </p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
      
      <!-- Phase 1: Input -->
      <section v-if="currentPhase === 'input'" class="space-y-6 animate-fade-in">
        <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <h2 class="text-2xl font-semibold text-white mb-6">
            📝 Describe tu Proyecto
          </h2>
          
          <!-- File Upload -->
          <div class="mb-6">
            <label class="block text-blue-200 mb-3 font-medium">
              Sube documentos de requisitos (múltiples archivos soportados)
            </label>
            <div 
              class="border-2 border-dashed border-blue-400/50 rounded-xl p-8 text-center hover:border-blue-400 transition-colors cursor-pointer bg-white/5"
              @dragover.prevent="isDragging = true"
              @dragleave="isDragging = false"
              @drop.prevent="handleDrop"
              @click="$refs.fileInput.click()"
            >
              <input 
                ref="fileInput" 
                type="file" 
                multiple 
                accept=".pdf,.docx,.md,.txt,.png,.jpg,.jpeg"
                class="hidden"
                @change="handleFileSelect"
              />
              <div class="text-blue-300">
                <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m0-3v12"/>
                </svg>
                <p class="text-lg">Arrastra archivos aquí o haz click para seleccionar</p>
                <p class="text-sm mt-2 text-blue-400">PDF, DOCX, MD, TXT, Imágenes (PNG, JPG)</p>
              </div>
            </div>
            
            <!-- Uploaded Files List -->
            <div v-if="uploadedFiles.length > 0" class="mt-4 space-y-2">
              <div v-for="(file, index) in uploadedFiles" :key="index" 
                   class="flex items-center justify-between bg-white/5 rounded-lg p-3">
                <span class="text-blue-200 truncate">{{ file.name }}</span>
                <button @click="removeFile(index)" class="text-red-400 hover:text-red-300">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Project Type -->
          <div class="mb-6">
            <label class="block text-blue-200 mb-3 font-medium">Tipo de Proyecto</label>
            <div class="flex gap-4">
              <button 
                @click="projectType = 'proposal'"
                :class="projectType === 'proposal' ? 'bg-blue-600 text-white' : 'bg-white/10 text-blue-200 hover:bg-white/20'"
                class="px-6 py-3 rounded-lg font-medium transition-colors flex-1"
              >
                📄 Propuesta Europea
              </button>
              <button 
                @click="projectType = 'code'"
                :class="projectType === 'code' ? 'bg-blue-600 text-white' : 'bg-white/10 text-blue-200 hover:bg-white/20'"
                class="px-6 py-3 rounded-lg font-medium transition-colors flex-1"
              >
                💻 Desarrollo de Código
              </button>
            </div>
          </div>
          
          <!-- Objective Input -->
          <div class="mb-6">
            <label class="block text-blue-200 mb-3 font-medium">
              Objetivo Principal del Proyecto *
            </label>
            <textarea 
              v-model="objective"
              rows="6"
              class="w-full bg-white/10 border border-white/20 rounded-xl p-4 text-white placeholder-blue-300/50 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="Describe detalladamente qué quieres lograr. Sé lo más específico posible..."
            ></textarea>
          </div>
          
          <!-- Analyze Button -->
          <button 
            @click="analyzeProject"
            :disabled="!objective || isAnalyzing"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold py-4 px-8 rounded-xl transition-all transform hover:scale-[1.02] disabled:transform-none disabled:cursor-not-allowed"
          >
            {{ isAnalyzing ? '🔄 Analizando...' : '🚀 Analizar Proyecto y Crear Agentes' }}
          </button>
        </div>
      </section>

      <!-- Phase 2: Configuration -->
      <section v-if="currentPhase === 'configuration'" class="space-y-6 animate-fade-in">
        <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <h2 class="text-2xl font-semibold text-white mb-2">
            ⚙️ Configuración del Equipo de Agentes
          </h2>
          <p class="text-blue-200 mb-6">
            Revisa y ajusta la configuración propuesta por el agente arquitecto
          </p>
          
          <!-- Project Analysis -->
          <div class="mb-8 p-6 bg-blue-900/30 rounded-xl border border-blue-500/30">
            <h3 class="text-lg font-semibold text-blue-200 mb-3">📊 Análisis del Proyecto</h3>
            <p class="text-white whitespace-pre-wrap">{{ analysisResult.project_analysis }}</p>
            <div class="mt-4 flex gap-4 text-sm">
              <span class="text-blue-300">
                Complejidad: <strong class="text-white">{{ analysisResult.complexity_score }}/10</strong>
              </span>
              <span class="text-blue-300">
                Tareas estimadas: <strong class="text-white">{{ analysisResult.estimated_tasks }}</strong>
              </span>
            </div>
          </div>
          
          <!-- Agents Configuration -->
          <div class="space-y-4 mb-8">
            <h3 class="text-lg font-semibold text-blue-200">🤖 Agentes Especializados</h3>
            
            <div v-for="(agent, index) in analysisResult.agents" :key="agent.id || index"
                 class="bg-white/5 rounded-xl p-6 border border-white/10 hover:border-blue-400/50 transition-colors">
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h4 class="text-xl font-semibold text-white">{{ agent.name || `Agente ${index + 1}` }}</h4>
                  <p class="text-blue-300">{{ agent.role }}</p>
                </div>
                <span class="px-3 py-1 bg-blue-600/50 rounded-full text-xs text-blue-200">
                  {{ agent.model || 'mistral:7b' }}
                </span>
              </div>
              
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <p class="text-blue-300 text-sm mb-2">Tareas:</p>
                  <ul class="space-y-1">
                    <li v-for="(task, tIndex) in agent.tasks" :key="tIndex" 
                        class="text-white text-sm flex items-start">
                      <span class="text-blue-400 mr-2">•</span>
                      {{ task }}
                    </li>
                  </ul>
                </div>
                
                <div>
                  <p class="text-blue-300 text-sm mb-2">Criterios de Calidad:</p>
                  <ul class="space-y-1">
                    <li v-for="(criteria, cIndex) in agent.quality_criteria || []" :key="cIndex" 
                        class="text-white text-sm flex items-start">
                      <span class="text-green-400 mr-2">✓</span>
                      {{ criteria }}
                    </li>
                  </ul>
                </div>
              </div>
              
              <!-- Model Selector -->
              <div class="mt-4 pt-4 border-t border-white/10">
                <label class="block text-blue-300 text-sm mb-2">Modelo IA:</label>
                <select 
                  v-model="agent.model"
                  class="bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="llama3:70b">Llama3 70B (Análisis complejo)</option>
                  <option value="codellama:34b">CodeLlama 34B (Código)</option>
                  <option value="mistral:7b">Mistral 7B (Rápido)</option>
                  <option value="llava:13b">LLaVA 13B (Imágenes)</option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Workflow Preview -->
          <div class="mb-8 p-6 bg-purple-900/30 rounded-xl border border-purple-500/30">
            <h3 class="text-lg font-semibold text-purple-200 mb-3">🔄 Workflow Propuesto</h3>
            <div class="flex flex-wrap gap-2 items-center">
              <template v-for="(step, index) in analysisResult.workflow || ['Análisis → Especialistas → Verificación → Edición']" :key="index">
                <span class="px-4 py-2 bg-purple-600/50 rounded-lg text-purple-100 text-sm">{{ step }}</span>
                <span v-if="index < (analysisResult.workflow?.length || 1) - 1" class="text-purple-300">→</span>
              </template>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex gap-4">
            <button 
              @click="currentPhase = 'input'"
              class="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium transition-colors"
            >
              ← Volver
            </button>
            <button 
              @click="executeProject"
              :disabled="isExecuting"
              class="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold py-4 px-8 rounded-xl transition-all transform hover:scale-[1.02] disabled:transform-none"
            >
              {{ isExecuting ? '⚡ Ejecutando...' : '✅ Confirmar y Ejecutar' }}
            </button>
          </div>
        </div>
      </section>

      <!-- Phase 3: Execution Progress -->
      <section v-if="currentPhase === 'execution'" class="space-y-6 animate-fade-in">
        <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <h2 class="text-2xl font-semibold text-white mb-6">
            ⚡ Ejecución en Progreso
          </h2>
          
          <!-- Progress Steps -->
          <div class="mb-8">
            <div class="flex items-center justify-between relative">
              <div class="absolute left-0 top-1/2 w-full h-1 bg-white/10 -z-10"></div>
              <div 
                class="absolute left-0 top-1/2 h-1 bg-gradient-to-r from-blue-500 to-green-500 -z-10 transition-all duration-500"
                :style="{ width: progressPercentage + '%' }"
              ></div>
              
              <div v-for="(phase, index) in phases" :key="phase"
                   :class="getPhaseClass(index)"
                   class="relative z-10 w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all duration-300"
              >
                {{ index + 1 }}
              </div>
            </div>
            
            <div class="flex justify-between mt-3 text-sm">
              <span v-for="phase in phases" :key="phase" 
                    class="text-blue-200 w-24 text-center">{{ phase }}</span>
            </div>
          </div>
          
          <!-- Current Status -->
          <div class="bg-blue-900/30 rounded-xl p-6 border border-blue-500/30 mb-6">
            <div class="flex items-center gap-4 mb-4">
              <div class="animate-spin w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full"></div>
              <h3 class="text-lg font-semibold text-blue-200">Fase Actual: {{ currentPhaseName }}</h3>
            </div>
            
            <p class="text-white mb-4">{{ phaseDescription }}</p>
            
            <!-- Verification Progress -->
            <div v-if="currentPhase === 'verification'" class="mt-4">
              <div class="flex justify-between text-sm text-blue-300 mb-2">
                <span>Iteración {{ verificationIteration }} de 5</span>
                <span>{{ (verificationIteration / 5 * 100).toFixed(0) }}%</span>
              </div>
              <div class="w-full bg-white/10 rounded-full h-3">
                <div 
                  class="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                  :style="{ width: (verificationIteration / 5 * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
          
          <!-- Logs -->
          <div class="bg-black/30 rounded-xl p-4 max-h-64 overflow-y-auto font-mono text-sm">
            <div v-for="(log, index) in logs" :key="index" class="text-green-400 mb-1">
              <span class="text-gray-500">[{{ log.time }}]</span> {{ log.message }}
            </div>
          </div>
        </div>
      </section>

      <!-- Phase 4: Results -->
      <section v-if="currentPhase === 'results'" class="space-y-6 animate-fade-in">
        <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <h2 class="text-2xl font-semibold text-white mb-6">
            ✅ Resultado Final
          </h2>
          
          <!-- Metadata -->
          <div class="grid md:grid-cols-3 gap-4 mb-6">
            <div class="bg-green-900/30 rounded-xl p-4 border border-green-500/30">
              <p class="text-green-200 text-sm">Iteraciones de Verificación</p>
              <p class="text-2xl font-bold text-white">{{ resultMetadata.iterations || 5 }}</p>
            </div>
            <div class="bg-blue-900/30 rounded-xl p-4 border border-blue-500/30">
              <p class="text-blue-200 text-sm">Issues Encontrados y Corregidos</p>
              <p class="text-2xl font-bold text-white">{{ resultMetadata.issuesFound || 0 }}</p>
            </div>
            <div class="bg-purple-900/30 rounded-xl p-4 border border-purple-500/30">
              <p class="text-purple-200 text-sm">Tiempo Total</p>
              <p class="text-2xl font-bold text-white">{{ resultMetadata.duration || '~' }}</p>
            </div>
          </div>
          
          <!-- Result Content -->
          <div class="bg-white/5 rounded-xl p-6 border border-white/10 mb-6 max-h-96 overflow-y-auto">
            <pre class="text-white whitespace-pre-wrap font-sans text-sm">{{ finalResult }}</pre>
          </div>
          
          <!-- Download Button -->
          <div class="flex gap-4">
            <button 
              @click="downloadResult"
              class="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-4 px-8 rounded-xl transition-all transform hover:scale-[1.02]"
            >
              📥 Descargar Resultado
            </button>
            <button 
              @click="currentPhase = 'input'"
              class="px-6 py-4 bg-white/10 hover:bg-white/20 text-white rounded-xl font-medium transition-colors"
            >
              🔄 Nuevo Proyecto
            </button>
          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE = '/api/v1'

export default {
  name: 'App',
  data() {
    return {
      currentPhase: 'input', // input, configuration, execution, results
      isDragging: false,
      uploadedFiles: [],
      projectType: 'proposal', // proposal, code
      objective: '',
      isAnalyzing: false,
      isExecuting: false,
      analysisResult: {},
      projectId: null,
      phases: ['Análisis', 'Especialistas', 'Verificación', 'Edición'],
      currentPhaseIndex: 0,
      progressPercentage: 0,
      verificationIteration: 0,
      logs: [],
      finalResult: '',
      resultMetadata: {}
    }
  },
  computed: {
    currentPhaseName() {
      return this.phases[this.currentPhaseIndex] || 'Procesando'
    },
    phaseDescription() {
      const descriptions = {
        'Análisis': 'El agente arquitecto está analizando el proyecto...',
        'Especialistas': 'Los agentes especializados están trabajando en paralelo...',
        'Verificación': 'Verificación exhaustiva en 5 iteraciones para eliminar alucinaciones...',
        'Edición': 'Formateo final y verificación de sintaxis...'
      }
      return descriptions[this.currentPhaseName] || 'Procesando...'
    }
  },
  methods: {
    handleDrop(e) {
      this.isDragging = false
      const files = Array.from(e.dataTransfer.files)
      this.addFiles(files)
    },
    handleFileSelect(e) {
      const files = Array.from(e.target.files)
      this.addFiles(files)
    },
    addFiles(files) {
      files.forEach(file => {
        if (!this.uploadedFiles.find(f => f.name === file.name)) {
          this.uploadedFiles.push(file)
        }
      })
    },
    removeFile(index) {
      this.uploadedFiles.splice(index, 1)
    },
    async analyzeProject() {
      this.isAnalyzing = true
      this.addLog('Iniciando análisis del proyecto...')
      
      try {
        const formData = new FormData()
        formData.append('objective', this.objective)
        formData.append('project_type', this.projectType)
        
        this.uploadedFiles.forEach(file => {
          formData.append('uploaded_files', file)
        })
        
        const response = await axios.post(`${API_BASE}/analyze`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        this.analysisResult = response.data
        this.addLog(`Análisis completado. ${this.analysisResult.agents?.length || 0} agentes propuestos.`)
        this.currentPhase = 'configuration'
        
      } catch (error) {
        console.error('Analysis error:', error)
        this.addLog('❌ Error en el análisis: ' + error.message)
        alert('Error al analizar el proyecto. Por favor, inténtalo de nuevo.')
      } finally {
        this.isAnalyzing = false
      }
    },
    async executeProject() {
      this.isExecuting = true
      this.projectId = 'proj_' + Date.now()
      this.currentPhase = 'execution'
      this.currentPhaseIndex = 0
      this.progressPercentage = 0
      
      this.addLog('Iniciando ejecución del proyecto...')
      
      try {
        const response = await axios.post(`${API_BASE}/execute/${this.projectId}`, {
          agent_configs: this.analysisResult,
          context: this.objective
        })
        
        this.addLog('Ejecución iniciada en background')
        
        // Poll for status
        this.pollStatus()
        
      } catch (error) {
        console.error('Execution error:', error)
        this.addLog('❌ Error en la ejecución: ' + error.message)
        this.isExecuting = false
      }
    },
    async pollStatus() {
      const maxPolls = 100
      let polls = 0
      
      const poll = async () => {
        if (polls >= maxPolls) {
          this.addLog('⚠️ Tiempo de espera agotado')
          this.isExecuting = false
          return
        }
        
        try {
          const response = await axios.get(`${API_BASE}/status/${this.projectId}`)
          const status = response.data
          
          this.updateProgress(status)
          
          if (status.status === 'completed') {
            this.addLog('✅ ¡Proyecto completado exitosamente!')
            await this.fetchResult()
            this.isExecuting = false
            this.currentPhase = 'results'
          } else if (status.status === 'failed') {
            this.addLog('❌ Error en la ejecución: ' + status.error)
            this.isExecuting = false
          } else {
            setTimeout(poll, 3000)
          }
        } catch (error) {
          console.error('Poll error:', error)
          setTimeout(poll, 3000)
        }
        
        polls++
      }
      
      poll()
    },
    updateProgress(status) {
      const phaseMap = {
        'specialists': 1,
        'compilation': 2,
        'verification': 3,
        'editing': 4
      }
      
      const phaseIndex = phaseMap[status.current_phase] || 0
      this.currentPhaseIndex = phaseIndex
      this.progressPercentage = ((phaseIndex + 1) / this.phases.length) * 100
      
      if (status.current_phase === 'verification' && status.verification_progress) {
        this.verificationIteration = status.verification_progress.iteration
      }
      
      this.addLog(`Fase actual: ${status.current_phase}`)
    },
    async fetchResult() {
      try {
        const response = await axios.get(`${API_BASE}/result/${this.projectId}`)
        this.finalResult = response.data.content
        this.resultMetadata = response.data.metadata
        
        // Calculate duration
        if (response.data.metadata.started_at && response.data.metadata.completed_at) {
          const start = new Date(response.data.metadata.started_at)
          const end = new Date(response.data.metadata.completed_at)
          const duration = Math.round((end - start) / 1000)
          this.resultMetadata.duration = `${duration}s`
        }
        
      } catch (error) {
        console.error('Fetch result error:', error)
        this.addLog('⚠️ No se pudo obtener el resultado completo')
      }
    },
    downloadResult() {
      const blob = new Blob([this.finalResult], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `resultado_${this.projectId}.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },
    addLog(message) {
      const time = new Date().toLocaleTimeString()
      this.logs.push({ time, message })
      // Keep only last 50 logs
      if (this.logs.length > 50) {
        this.logs.shift()
      }
    },
    getPhaseClass(index) {
      if (index < this.currentPhaseIndex) {
        return 'bg-green-500 text-white'
      } else if (index === this.currentPhaseIndex) {
        return 'bg-blue-500 text-white scale-110'
      } else {
        return 'bg-white/10 text-blue-300'
      }
    }
  }
}
</script>

<style scoped>
/* Additional scoped styles if needed */
</style>
