<template>
  <div class="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-white mb-4">Describe tu Proyecto</h2>
      <textarea 
        v-model="description"
        placeholder="Ej: Quiero crear una propuesta para Horizon Europe sobre inteligencia artificial aplicada a la sostenibilidad..."
        class="w-full h-48 px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
      ></textarea>
    </div>

    <div class="space-y-3">
      <label class="block text-white font-medium">Documentos de referencia (opcional)</label>
      <div 
        class="border-2 border-dashed border-white/30 rounded-lg p-8 text-center hover:border-white/50 transition-colors cursor-pointer"
        @dragover.prevent
        @drop="handleDrop"
        @click="$refs.fileInput.click()"
      >
        <input 
          ref="fileInput"
          type="file" 
          multiple 
          accept=".pdf,.docx,.md,.png,.jpg,.jpeg"
          class="hidden"
          @change="handleFileSelect"
        />
        <svg class="w-12 h-12 mx-auto text-blue-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m0-3v12"/>
        </svg>
        <p class="text-blue-200 mb-2">Arrastra archivos aquí o haz clic para seleccionar</p>
        <p class="text-sm text-blue-300">Soporta: PDF, DOCX, MD, imágenes (OCR)</p>
      </div>

      <!-- Lista de archivos subidos -->
      <div v-if="files.length > 0" class="space-y-2">
        <div v-for="(file, index) in files" :key="index" class="flex items-center justify-between bg-white/10 rounded-lg px-4 py-2">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <span class="text-white">{{ file.name }}</span>
            <span class="text-xs text-blue-300">({{ formatFileSize(file.size) }})</span>
          </div>
          <button @click.stop="removeFile(index)" class="text-red-300 hover:text-red-100">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div class="flex justify-end">
      <button 
        @click="handleSubmit"
        :disabled="!description.trim()"
        class="px-8 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
      >
        <span class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          Analizar Proyecto
        </span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectInput',
  emits: ['submit'],
  data() {
    return {
      description: '',
      files: []
    };
  },
  methods: {
    handleFileSelect(event) {
      const newFiles = Array.from(event.target.files);
      this.files.push(...newFiles);
    },
    handleDrop(event) {
      const droppedFiles = Array.from(event.dataTransfer.files);
      this.files.push(...droppedFiles);
    },
    removeFile(index) {
      this.files.splice(index, 1);
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    },
    handleSubmit() {
      if (!this.description.trim()) return;
      
      this.$emit('submit', {
        description: this.description,
        files: this.files
      });
    }
  }
};
</script>
