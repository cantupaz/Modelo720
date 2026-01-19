import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Parse from '../views/Parse.vue'
import Convert from '../views/Convert.vue'
import ViewDeclaration from '../views/ViewDeclaration.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/parse',
    name: 'Parse',
    component: Parse
  },
  {
    path: '/convert',
    name: 'Convert',
    component: Convert
  },
  {
    path: '/view/:id',
    name: 'ViewDeclaration',
    component: ViewDeclaration
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
