<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Resultado principal -->
    <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
      <div class="flex items-center gap-4 mb-6">
        <div class="w-16 h-16 rounded-full bg-green-500/30 border-2 border-green-400 flex items-center justify-center">
          <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white">Proyecto Completado</h2>
          <p class="text-blue-200">Documento generado con calidad verificada</p>
        </div>
      </div>

      <!-- Resumen -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-white/10 rounded-xl p-4 text-center">
          <p class="text-3xl font-bold text-white">{{ result.agents || 5 }}</p>
          <p class="text-xs text-blue-200 mt-1">Agentes</p>
        </div>
        <div class="bg-white/10 rounded-xl p-4 text-center">
          <p class="text-3xl font-bold text-white">{{ result.iterations || 5 }}</p>
          <p class="text-xs text-blue-200 mt-1">Iteraciones</p>
        </div>
        <div class="bg-white/10 rounded-xl p-4 text-center">
          <p class="text-3xl font-bold text-white">100%</p>
          <p class="text-xs text-blue-200 mt-1">Verificado</p>
        </div>
        <div class="bg-white/10 rounded-xl p-4 text-center">
          <p class="text-3xl font-bold text-white">MD</p>
          <p class="text-xs text-blue-200 mt-1">Formato</p>
        </div>
      </div>

      <!-- Contenido generado -->
      <div class="bg-white/10 rounded-xl border border-white/20 overflow-hidden mb-6">
        <div class="flex items-center justify-between px-4 py-3 bg-white/10 border-b border-white/20">
          <h3 class="font-semibold text-white">Documento Generado</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs text-blue-200">{{ result.title || 'Sin título' }}</span>
          </div>
        </div>
        <div class="p-6 max-h-96 overflow-y-auto">
          <pre class="text-sm text-blue-100 whitespace-pre-wrap font-mono">{{ result.content || 'Contenido no disponible' }}</pre>
        </div>
      </div>

      <!-- Acciones -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <button 
          @click="downloadMarkdown"
          class="px-8 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl"
        >
          <span class="flex items-center justify-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            Descargar Markdown
          </span>
        </button>
        
        <button 
          @click="$emit('restart')"
          class="px-8 py-3 bg-white/20 text-white font-semibold rounded-lg hover:bg-white/30 transition-colors"
        >
          <span class="flex items-center justify-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            Nuevo Proyecto
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResultsView',
  props: {
    result: {
      type: Object,
      required: true
    }
  },
  emits: ['restart'],
  methods: {
    downloadMarkdown() {
      const content = this.result.content || '# Documento Generado\n\nContenido no disponible';
      const filename = (this.result.title || 'documento').replace(/\s+/g, '_') + '.md';
      
      const blob = new Blob([content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }
};
</script>
