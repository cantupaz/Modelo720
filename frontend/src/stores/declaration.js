import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDeclarationStore = defineStore('declaration', () => {
  // State
  const currentDeclaration = ref(null)
  const declarations = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const hasDeclaration = computed(() => currentDeclaration.value !== null)
  const detalleCount = computed(() => 
    currentDeclaration.value?.detalles?.length || 0
  )

  // Actions
  function setDeclaration(declaration) {
    currentDeclaration.value = declaration
    // Add to history if not already there
    const id = Date.now()
    declarations.value.unshift({
      id,
      declaration,
      timestamp: new Date()
    })
    // Keep only last 10
    if (declarations.value.length > 10) {
      declarations.value = declarations.value.slice(0, 10)
    }
  }

  function clearDeclaration() {
    currentDeclaration.value = null
  }

  function setLoading(value) {
    loading.value = value
  }

  function setError(errorMessage) {
    error.value = errorMessage
  }

  function clearError() {
    error.value = null
  }

  function getDeclarationById(id) {
    return declarations.value.find(d => d.id === parseInt(id))
  }

  return {
    // State
    currentDeclaration,
    declarations,
    loading,
    error,
    // Getters
    hasDeclaration,
    detalleCount,
    // Actions
    setDeclaration,
    clearDeclaration,
    setLoading,
    setError,
    clearError,
    getDeclarationById
  }
})
