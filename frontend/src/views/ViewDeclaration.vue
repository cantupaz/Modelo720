<template>
  <div class="view-declaration">
    <div v-if="loading" class="loading-container">
      <span class="loading"></span>
      <p>Cargando...</p>
    </div>

    <div v-else-if="!declaration">
      <div class="error">
        Declaración no encontrada
      </div>
      <router-link to="/">
        <button class="primary">Volver al inicio</button>
      </router-link>
    </div>

    <div v-else>
      <DeclarationViewer :declaration="declaration.declaration" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDeclarationStore } from '../stores/declaration'
import DeclarationViewer from '../components/DeclarationViewer.vue'

const route = useRoute()
const store = useDeclarationStore()
const declaration = ref(null)
const loading = ref(true)

onMounted(() => {
  const id = route.params.id
  declaration.value = store.getDeclarationById(id)
  loading.value = false
})
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
}
</style>
