<template>
  <div class="home">
    <div class="hero">
      <h1>Modelo 720</h1>
      <p class="subtitle">Gestión de Declaraciones de Bienes y Derechos en el Extranjero</p>
    </div>

    <div class="features">
      <div class="card feature">
        <h3>📄 Analizar Declaraciones</h3>
        <p>Carga archivos .720 o CSV para visualizar y validar tus declaraciones</p>
        <router-link to="/parse">
          <button class="primary">Analizar Archivo</button>
        </router-link>
      </div>

      <div class="card feature">
        <h3>🔄 Convertir Formatos</h3>
        <p>Convierte entre el formato oficial .720 y CSV para facilitar la edición</p>
        <router-link to="/convert">
          <button class="primary">Convertir Formato</button>
        </router-link>
      </div>

      <div class="card feature">
        <h3>✅ Validar Datos</h3>
        <p>Verifica que tu declaración cumple todos los requisitos antes de presentarla</p>
        <router-link to="/parse">
          <button class="primary">Validar</button>
        </router-link>
      </div>
    </div>

    <div class="card info">
      <h2>Acerca del Modelo 720</h2>
      <p>
        El Modelo 720 es una declaración informativa sobre bienes y derechos situados en el extranjero 
        que deben presentar los contribuyentes residentes en España.
      </p>
      <ul>
        <li><strong>Cuentas bancarias</strong> (Clave C)</li>
        <li><strong>Valores, derechos y seguros</strong> (Clave V)</li>
        <li><strong>Inmuebles</strong> (Clave I)</li>
      </ul>
    </div>

    <div v-if="store.declarations.length > 0" class="card">
      <h2>Historial Reciente</h2>
      <div class="history">
        <div 
          v-for="item in store.declarations.slice(0, 5)" 
          :key="item.id"
          class="history-item"
        >
          <div class="history-info">
            <strong>{{ item.declaration.header.nombre_razon }}</strong>
            <span class="text-muted">
              {{ item.declaration.header.ejercicio }} - 
              {{ item.declaration.detalles.length }} bienes
            </span>
          </div>
          <router-link :to="`/view/${item.id}`">
            <button class="secondary">Ver</button>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDeclarationStore } from '../stores/declaration'

const store = useDeclarationStore()
</script>

<style scoped>
.hero {
  text-align: center;
  margin: 3rem 0;
}

.subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.5rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.feature {
  text-align: center;
}

.feature h3 {
  margin-bottom: 1rem;
}

.feature p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 1.5rem;
}

.info {
  margin: 2rem 0;
}

.info ul {
  margin-top: 1rem;
  padding-left: 2rem;
}

.info li {
  margin: 0.5rem 0;
}

.history {
  margin-top: 1rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #333;
}

.history-item:last-child {
  border-bottom: none;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.text-muted {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

@media (prefers-color-scheme: light) {
  .subtitle {
    color: #666;
  }
  
  .feature p {
    color: #666;
  }
  
  .text-muted {
    color: #999;
  }
  
  .history-item {
    border-bottom-color: #e5e5e5;
  }
}
</style>
