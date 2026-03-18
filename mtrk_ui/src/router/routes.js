
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: 'inspector' },
      { path: 'inspector', component: () => import('pages/Inspector.vue') },
      { path: 'generator', component: () => import('pages/Generator.vue') },
      { path: 'simulator', component: () => import('pages/Simulator.vue') },
      { path: 'settings', component: () => import('pages/Settings.vue') }
    ]
  }
]

// Always leave this as last one
if (process.env.MODE !== 'ssr') {
  routes.push({
    path: '*',
    component: () => import('pages/Error404.vue')
  })
}

export default routes
