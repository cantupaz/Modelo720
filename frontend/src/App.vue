<template>
  <div id="app">
    <nav class="navbar">
      <div class="container">
        <div class="nav-content">
          <h1 class="logo">Modelo 720</h1>
          <div class="nav-links">
            <router-link to="/">Inicio</router-link>
            <router-link to="/parse">Analizar</router-link>
            <router-link to="/convert">Convertir</router-link>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="container">
      <router-view />
    </main>
    
    <footer>
      <div class="container">
        <p>&copy; 2026 Modelo 720 App - Gestión de Declaraciones de Bienes en el Extranjero</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.navbar {
  background: #1a1a1a;
  border-bottom: 1px solid #333;
  padding: 1rem 0;
  margin-bottom: 2rem;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  margin: 0;
  font-size: 1.5rem;
  color: #646cff;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  color: rgba(255, 255, 255, 0.87);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.25s;
}

.nav-links a:hover {
  color: #646cff;
}

.nav-links a.router-link-active {
  color: #646cff;
}

footer {
  margin-top: 4rem;
  padding: 2rem 0;
  border-top: 1px solid #333;
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
}

@media (prefers-color-scheme: light) {
  .navbar {
    background: #f9f9f9;
    border-bottom-color: #e5e5e5;
  }
  
  .nav-links a {
    color: #213547;
  }
  
  footer {
    border-top-color: #e5e5e5;
    color: #666;
  }
}
</style>
