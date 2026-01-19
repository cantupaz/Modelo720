<template>
  <div class="convert">
    <h1>Convertir Formato</h1>
    <p>Convierte entre el formato oficial .720 y CSV</p>

    <div class="card">
      <h2>Seleccionar Archivo</h2>
      
      <div class="format-selector">
        <label>
          <input type="radio" v-model="sourceFormat" value="720" />
          Desde .720 a CSV
        </label>
        <label>
          <input type="radio" v-model="sourceFormat" value="csv" />
          Desde CSV a .720
        </label>
      </div>

      <div class="upload-zone" @click="triggerFileInput">
        <input 
          type="file" 
          ref="fileInput"
          @change="handleFileChange"
          :accept="sourceFormat === '720' ? '.720' : '.csv'"
        />
        <div v-if="!selectedFile" class="upload-prompt">
          <span class="upload-icon">📁</span>
          <p>Haz clic para seleccionar archivo</p>
          <p class="text-muted">{{ sourceFormat === '720' ? 'Archivo .720' : 'Archivo CSV' }}</p>
        </div>
        <div v-else class="file-selected">
          <span class="upload-icon">✅</span>
          <p><strong>{{ selectedFile.name }}</strong></p>
          <p class="text-muted">{{ formatFileSize(selectedFile.size) }}</p>
        </div>
      </div>

      <button 
        class="primary"
        @click="convertFile"
        :disabled="!selectedFile || loading"
        style="margin-top: 1rem; width: 100%;"
      >
        <span v-if="loading" class="loading"></span>
        <span v-else>Convertir</span>
      </button>

      <div v-if="error" class="error" style="margin-top: 1rem;">
        {{ error }}
      </div>

      <div v-if="success" class="success" style="margin-top: 1rem;">
        ✅ Archivo convertido y descargado correctamente
      </div>
    </div>

    <div class="card info">
      <h3>ℹ️ Información</h3>
      <p><strong>Formato .720:</strong> Formato oficial de ancho fijo usado por la Agencia Tributaria</p>
      <p><strong>Formato CSV:</strong> Formato de valores separados por comas, más fácil de editar en Excel u otras herramientas</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { declarationsApi } from '../api/client'

const sourceFormat = ref('720')
const targetFormat = computed(() => sourceFormat.value === '720' ? 'csv' : '720')
const selectedFile = ref(null)
const fileInput = ref(null)
const loading = ref(false)
const error = ref(null)
const success = ref(null)

function triggerFileInput() {
  fileInput.value.click()
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    error.value = null
    success.value = null
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function convertFile() {
  if (!selectedFile.value) return

  loading.value = true
  error.value = null
  success.value = null

  try {
    const blob = await declarationsApi.convert(
      selectedFile.value,
      sourceFormat.value,
      targetFormat.value
    )

    // Download the file
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `converted.${targetFormat.value}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    success.value = true
    
    // Reset after 3 seconds
    setTimeout(() => {
      selectedFile.value = null
      fileInput.value.value = ''
      success.value = null
    }, 3000)

  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Error al convertir el archivo'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.convert {
  max-width: 800px;
  margin: 0 auto;
}

.convert > p {
  color: rgba(255, 255, 255, 0.7);
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

.upload-zone {
  border: 2px dashed #646cff;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-zone:hover {
  background-color: rgba(100, 108, 255, 0.1);
  border-color: #535bf2;
}

.upload-prompt,
.file-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.text-muted {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

.info {
  margin-top: 2rem;
}

.info p {
  margin: 0.75rem 0;
  line-height: 1.6;
}

@media (prefers-color-scheme: light) {
  .convert > p {
    color: #666;
  }
  
  .text-muted {
    color: #999;
  }
}
</style>
