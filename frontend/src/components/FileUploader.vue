<template>
  <div class="card file-uploader">
    <h2>Cargar Archivo</h2>
    
    <div class="format-selector">
      <label>
        <input type="radio" v-model="selectedFormat" value="720" />
        Archivo .720
      </label>
      <label>
        <input type="radio" v-model="selectedFormat" value="csv" />
        Archivo CSV
      </label>
    </div>

    <div 
      class="drop-zone"
      @dragover.prevent="dragover = true"
      @dragleave.prevent="dragover = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
      :class="{ 'dragover': dragover }"
    >
      <input 
        type="file" 
        ref="fileInput"
        @change="handleFileChange"
        :accept="selectedFormat === '720' ? '.720' : '.csv'"
      />
      
      <div v-if="!file" class="drop-prompt">
        <span class="icon">📂</span>
        <p>Arrastra y suelta un archivo aquí</p>
        <p class="or">o</p>
        <button class="secondary" @click.stop="triggerFileInput">
          Seleccionar Archivo
        </button>
        <p class="hint">{{ selectedFormat === '720' ? 'Archivo .720' : 'Archivo CSV' }}</p>
      </div>

      <div v-else class="file-info">
        <span class="icon">✅</span>
        <p><strong>{{ file.name }}</strong></p>
        <p class="file-size">{{ formatFileSize(file.size) }}</p>
        <button class="danger" @click.stop="clearFile">
          Eliminar
        </button>
      </div>
    </div>

    <button 
      class="primary upload-btn"
      @click="uploadFile"
      :disabled="!file || loading"
    >
      <span v-if="loading" class="loading"></span>
      <span v-else>Analizar Archivo</span>
    </button>

    <div v-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: Boolean,
  error: String
})

const emit = defineEmits(['file-selected'])

const selectedFormat = ref('720')
const file = ref(null)
const fileInput = ref(null)
const dragover = ref(false)

function triggerFileInput() {
  fileInput.value.click()
}

function handleFileChange(event) {
  const selectedFile = event.target.files[0]
  if (selectedFile) {
    file.value = selectedFile
  }
}

function handleDrop(event) {
  dragover.value = false
  const droppedFile = event.dataTransfer.files[0]
  if (droppedFile) {
    file.value = droppedFile
  }
}

function clearFile() {
  file.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function uploadFile() {
  if (file.value) {
    emit('file-selected', file.value, selectedFormat.value)
  }
}
</script>

<style scoped>
.file-uploader {
  margin-bottom: 2rem;
}

.format-selector {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.format-selector label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.format-selector input[type="radio"] {
  cursor: pointer;
}

.drop-zone {
  border: 2px dashed #646cff;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 1rem;
}

.drop-zone:hover,
.drop-zone.dragover {
  background-color: rgba(100, 108, 255, 0.1);
  border-color: #535bf2;
}

.drop-prompt,
.file-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.icon {
  font-size: 3rem;
}

.or {
  color: rgba(255, 255, 255, 0.5);
  margin: 0.5rem 0;
}

.hint {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.file-size {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.upload-btn {
  width: 100%;
}

@media (prefers-color-scheme: light) {
  .or,
  .hint,
  .file-size {
    color: #999;
  }
}
</style>
