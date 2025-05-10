import {
  createRouter,
  createWebHistory
} from 'vue-router'

export const routes = [{
    path: '/home',
    name: 'Home',
    chName: "远程下单",
    icon: "House",
    component: () => import('../views/home/index.vue'),
    redirect: '/home/list',
    children: [
      {
        path: '/home/detail',
        name: 'HomeDetail',
        component: () => import('../views/home/components/detail.vue')
      },
      {
        path: '/home/list',
        name: 'HomeList',
        component: () => import('../views/home/components/list.vue')
      }
    ]
  },
  {
    path: '/order',
    name: 'Order',
    chName: "订单列表",
    icon: "List",
    component: () => import('../views/order/index.vue')
  },
  {
    path: '/setting',
    name: 'Setting',
    chName: "设置",
    icon: "Setting",
    component: () => import('../views/setting/index.vue')
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router