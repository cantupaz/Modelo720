<template>
  <div class="declaration-viewer">
    <div class="card">
      <div class="header-actions">
        <h2>Declaración</h2>
        <div class="actions">
          <button class="secondary" @click="exportDeclaration('csv')">
            Exportar CSV
          </button>
          <button class="primary" @click="exportDeclaration('720')">
            Exportar .720
          </button>
        </div>
      </div>

      <div class="header-info">
        <div class="info-grid">
          <div class="info-item">
            <label>Modelo:</label>
            <span>{{ declaration.header.modelo }}</span>
          </div>
          <div class="info-item">
            <label>Ejercicio:</label>
            <span>{{ declaration.header.ejercicio }}</span>
          </div>
          <div class="info-item">
            <label>NIF Declarante:</label>
            <span>{{ declaration.header.nif_declarante }}</span>
          </div>
          <div class="info-item">
            <label>Nombre/Razón Social:</label>
            <span>{{ declaration.header.nombre_razon }}</span>
          </div>
          <div class="info-item">
            <label>Número Identificativo:</label>
            <span>{{ declaration.header.numero_identificativo }}</span>
          </div>
          <div class="info-item">
            <label>Total Registros:</label>
            <span>{{ declaration.header.numero_total_registros }}</span>
          </div>
          <div class="info-item">
            <label>Suma Valoración 1:</label>
            <span>{{ formatAmount(declaration.header.suma_valoracion_1) }}</span>
          </div>
          <div class="info-item">
            <label>Suma Valoración 2:</label>
            <span>{{ formatAmount(declaration.header.suma_valoracion_2) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>Detalles de Bienes ({{ declaration.detalles.length }})</h2>
      
      <div v-if="declaration.detalles.length === 0" class="no-data">
        No hay bienes declarados
      </div>

      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Tipo</th>
              <th>País</th>
              <th>Titular</th>
              <th>Origen</th>
              <th>Valoración 1</th>
              <th>Valoración 2</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(detalle, index) in declaration.detalles" :key="index">
              <td>{{ index + 1 }}</td>
              <td>
                <span class="badge" :class="`badge-${detalle.clave_tipo_bien}`">
                  {{ getBienLabel(detalle.clave_tipo_bien) }}
                </span>
              </td>
              <td>{{ detalle.codigo_pais }}</td>
              <td>{{ detalle.nombre_razon_declarado }}</td>
              <td>
                <span class="badge-origen">{{ getOrigenLabel(detalle.origen) }}</span>
              </td>
              <td>{{ formatAmount(detalle.valoracion_1) }}</td>
              <td>{{ formatAmount(detalle.valoracion_2) }}</td>
              <td>
                <button class="secondary small" @click="viewDetail(index)">
                  Ver
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedDetail !== null" class="modal" @click.self="closeDetail">
      <div class="modal-content card">
        <div class="modal-header">
          <h2>Detalle del Bien #{{ selectedDetail + 1 }}</h2>
          <button class="close-btn" @click="closeDetail">✕</button>
        </div>
        <div class="detail-info">
          <DetailView :detalle="declaration.detalles[selectedDetail]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { declarationsApi } from '../api/client'
import DetailView from './DetailView.vue'

const props = defineProps({
  declaration: {
    type: Object,
    required: true
  }
})

const selectedDetail = ref(null)
const exporting = ref(false)

function formatAmount(valoracion) {
  if (!valoracion) return '0.00 €'
  const amount = parseFloat(valoracion.importe)
  return `${amount.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`
}

function getBienLabel(clave) {
  const labels = {
    'C': 'Cuenta',
    'V': 'Valores',
    'I': 'Inmueble',
    'S': 'Seguro',
    'B': 'Bien mueble'
  }
  return labels[clave] || clave
}

function getOrigenLabel(origen) {
  const labels = {
    'A': 'Adquisición',
    'M': 'Modificación',
    'C': 'Cancelación'
  }
  return labels[origen] || origen
}

function viewDetail(index) {
  selectedDetail.value = index
}

function closeDetail() {
  selectedDetail.value = null
}

async function exportDeclaration(format) {
  if (exporting.value) return
  
  exporting.value = true
  try {
    const blob = await declarationsApi.export(props.declaration, format)
    
    // Download file
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `modelo720_${props.declaration.header.ejercicio}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting:', error)
    alert('Error al exportar el archivo')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-actions h2 {
  margin: 0;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.info-item span {
  font-size: 1rem;
}

.table-container {
  overflow-x: auto;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.5);
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.badge-C { background: #1e40af; color: white; }
.badge-V { background: #15803d; color: white; }
.badge-I { background: #a21caf; color: white; }
.badge-S { background: #c2410c; color: white; }
.badge-B { background: #4338ca; color: white; }

.badge-origen {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

button.small {
  padding: 0.3rem 0.8rem;
  font-size: 0.85rem;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal-content {
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h2 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (prefers-color-scheme: light) {
  .info-item label {
    color: #666;
  }
  
  .no-data {
    color: #999;
  }
  
  .badge-origen {
    color: #666;
  }
}
</style>
