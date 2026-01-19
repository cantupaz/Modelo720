<template>
  <div class="detail-view">
    <div class="detail-grid">
      <div class="detail-item">
        <label>Tipo de Bien:</label>
        <span>{{ getBienLabel(detalle.clave_tipo_bien) }} ({{ detalle.clave_tipo_bien }})</span>
      </div>
      
      <div class="detail-item">
        <label>Subclave:</label>
        <span>{{ detalle.subclave }}</span>
      </div>

      <div class="detail-item">
        <label>Origen:</label>
        <span>{{ getOrigenLabel(detalle.origen) }}</span>
      </div>

      <div class="detail-item">
        <label>País:</label>
        <span>{{ detalle.codigo_pais }}</span>
      </div>

      <div class="detail-item">
        <label>NIF Declarado:</label>
        <span>{{ detalle.nif_declarado }}</span>
      </div>

      <div class="detail-item">
        <label>Titular:</label>
        <span>{{ detalle.nombre_razon_declarado }}</span>
      </div>

      <div class="detail-item" v-if="detalle.nif_representante">
        <label>NIF Representante:</label>
        <span>{{ detalle.nif_representante }}</span>
      </div>

      <div class="detail-item">
        <label>Clave Condición:</label>
        <span>{{ detalle.clave_condicion }}</span>
      </div>

      <div class="detail-item" v-if="detalle.codigo_cuenta">
        <label>Código Cuenta:</label>
        <span>{{ detalle.codigo_cuenta }}</span>
      </div>

      <div class="detail-item" v-if="detalle.identificacion_valores">
        <label>Identificación Valores:</label>
        <span>{{ detalle.identificacion_valores }}</span>
      </div>

      <div class="detail-item" v-if="detalle.identificacion_entidad">
        <label>Entidad:</label>
        <span>{{ detalle.identificacion_entidad }}</span>
      </div>

      <div class="detail-item" v-if="detalle.codigo_bic">
        <label>Código BIC:</label>
        <span>{{ detalle.codigo_bic }}</span>
      </div>

      <div class="detail-item" v-if="detalle.fecha_incorporacion">
        <label>Fecha Incorporación:</label>
        <span>{{ detalle.fecha_incorporacion }}</span>
      </div>

      <div class="detail-item" v-if="detalle.fecha_extincion">
        <label>Fecha Extinción:</label>
        <span>{{ detalle.fecha_extincion }}</span>
      </div>

      <div class="detail-item">
        <label>Valoración 1:</label>
        <span class="amount">{{ formatAmount(detalle.valoracion_1) }}</span>
      </div>

      <div class="detail-item">
        <label>Valoración 2:</label>
        <span class="amount">{{ formatAmount(detalle.valoracion_2) }}</span>
      </div>

      <div class="detail-item">
        <label>Participación:</label>
        <span>{{ detalle.porcentaje_participacion_entera }}.{{ String(detalle.porcentaje_participacion_decimal).padStart(2, '0') }}%</span>
      </div>

      <div class="detail-item" v-if="detalle.numero_valores_entera || detalle.numero_valores_decimal">
        <label>Número de Valores:</label>
        <span>{{ detalle.numero_valores_entera }}.{{ String(detalle.numero_valores_decimal).padStart(2, '0') }}</span>
      </div>
    </div>

    <div v-if="hasDomicilio" class="section">
      <h3>Domicilio</h3>
      <div class="detail-grid">
        <div class="detail-item" v-if="detalle.domicilio_via_num">
          <label>Vía y Número:</label>
          <span>{{ detalle.domicilio_via_num }}</span>
        </div>
        <div class="detail-item" v-if="detalle.domicilio_complemento">
          <label>Complemento:</label>
          <span>{{ detalle.domicilio_complemento }}</span>
        </div>
        <div class="detail-item" v-if="detalle.domicilio_poblacion">
          <label>Población:</label>
          <span>{{ detalle.domicilio_poblacion }}</span>
        </div>
        <div class="detail-item" v-if="detalle.domicilio_region">
          <label>Región:</label>
          <span>{{ detalle.domicilio_region }}</span>
        </div>
        <div class="detail-item" v-if="detalle.domicilio_cp">
          <label>Código Postal:</label>
          <span>{{ detalle.domicilio_cp }}</span>
        </div>
        <div class="detail-item" v-if="detalle.domicilio_pais">
          <label>País:</label>
          <span>{{ detalle.domicilio_pais }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  detalle: {
    type: Object,
    required: true
  }
})

const hasDomicilio = computed(() => {
  return props.detalle.domicilio_via_num || 
         props.detalle.domicilio_poblacion || 
         props.detalle.domicilio_pais
})

function formatAmount(valoracion) {
  if (!valoracion) return '0.00 €'
  const amount = parseFloat(valoracion.importe)
  return `${amount.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`
}

function getBienLabel(clave) {
  const labels = {
    'C': 'Cuenta Bancaria',
    'V': 'Valores y Derechos',
    'I': 'Inmueble',
    'S': 'Seguro',
    'B': 'Bien Mueble'
  }
  return labels[clave] || clave
}

function getOrigenLabel(origen) {
  const labels = {
    'A': 'Adquisición (Primera vez)',
    'M': 'Modificación',
    'C': 'Cancelación'
  }
  return labels[origen] || origen
}
</script>

<style scoped>
.detail-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section h3 {
  margin-bottom: 1rem;
  color: #646cff;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.detail-item span {
  font-size: 0.95rem;
}

.detail-item .amount {
  font-weight: 600;
  color: #22c55e;
}

@media (prefers-color-scheme: light) {
  .detail-item label {
    color: #666;
  }
}
</style>
