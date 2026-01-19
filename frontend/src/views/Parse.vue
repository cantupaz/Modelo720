<template>
  <div class="parse">
    <h1>Analizar Declaración</h1>
    <p>Carga un archivo .720 o CSV para visualizar y validar su contenido</p>

    <FileUploader 
      @file-selected="handleFileSelected"
      :loading="store.loading"
      :error="store.error"
    />

    <div v-if="validationResult" class="card">
      <h2>Resultado de Validación</h2>
      <div v-if="validationResult.valid" class="success">
        ✅ La declaración es válida
      </div>
      <div v-else class="error">
        <strong>❌ Errores encontrados:</strong>
        <ul>
          <li v-for="(error, index) in validationResult.errors" :key="index">
            {{ error }}
          </li>
        </ul>
      </div>
    </div>

    <DeclarationViewer 
      v-if="store.hasDeclaration"
      :declaration="store.currentDeclaration"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDeclarationStore } from '../stores/declaration'
import { declarationsApi } from '../api/client'
import FileUploader from '../components/FileUploader.vue'
import DeclarationViewer from '../components/DeclarationViewer.vue'

const store = useDeclarationStore()
const validationResult = ref(null)

async function handleFileSelected(file, format) {
  store.setLoading(true)
  store.clearError()
  validationResult.value = null

  try {
    // Parse the file
    const declaration = await declarationsApi.parse(file, format)
    store.setDeclaration(declaration)

    // Validate it
    const validation = await declarationsApi.validate(declaration)
    validationResult.value = validation

  } catch (error) {
    const message = error.response?.data?.detail || error.message || 'Error al procesar el archivo'
    store.setError(message)
  } finally {
    store.setLoading(false)
  }
}
</script>

<style scoped>
.parse {
  max-width: 1000px;
  margin: 0 auto;
}

.parse > p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 2rem;
}

.error ul {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.error li {
  margin: 0.25rem 0;
}

@media (prefers-color-scheme: light) {
  .parse > p {
    color: #666;
  }
}
</style>
