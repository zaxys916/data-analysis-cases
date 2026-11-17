import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('./views/Dashboard.vue') },
    { path: '/cases', name: 'cases', component: () => import('./views/CaseList.vue') },
    { path: '/cases/:id', name: 'case-detail', component: () => import('./views/CaseDetail.vue') },
  ],
})
