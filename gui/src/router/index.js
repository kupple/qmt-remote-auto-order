import { getSettingConfig } from '@/api/comm_tube'
import { fetchUserInfo } from '@/api/user'
import { clearAuth, getToken, getUserInfo, setUserInfo } from '@/utils/auth'
import { createRouter, createWebHashHistory } from 'vue-router'

export const routes = [
  {
    path: '/',
    name: 'Loading',
    component: () => import('../views/loading/index.vue'),
    meta: {
      title: '自动远程下单',
      show: false,
      showBack: false
    }
  },
  {
    path: '/home',
    name: 'Home',
    chName: '远程下单',
    icon: 'House',
    component: () => import('../views/home/index.vue'),
    redirect: '/home/list',
    children: [
      {
        path: '/home/detail',
        name: 'HomeDetail',
        component: () => import('../views/home/components/detail.vue'),
        meta: {
          title: '任务详情',
          showBack: true
        }
      },
      {
        path: '/home/list',
        name: 'HomeList',
        component: () => import('../views/home/components/list.vue'),
        meta: {
          title: '自动远程下单',
          showBack: false
        }
      }
    ]
  },
  {
    path: '/order',
    name: 'Order',
    chName: '订单列表',
    icon: 'List',
    component: () => import('../views/order/index.vue'),
    meta: {
      title: '订单列表',
      showBack: false
    }
  },
  {
    path: '/transition',
    name: 'Transition',
    chName: '一键转换',
    icon: 'Sort',
    show: false,
    component: () => import('../views/transition/index.vue'),
    meta: {
      title: '一键转换',
      showBack: true
    }
  },
  {
    path: '/setting',
    name: 'Setting',
    chName: '设置',
    icon: 'Setting',
    component: () => import('../views/setting/index.vue'),
    redirect: '/setting/login',
    children: [
      {
        path: '/setting/login',
        name: 'SettingCommunity',
        component: () => import('../views/setting/components/login.vue'),
        meta: {
          title: '登录',
          showBack: false
        }
      },
      {
        path: '/setting/register',
        name: 'SettingRegister',
        component: () => import('../views/setting/components/register.vue'),
        meta: {
          title: '注册',
          showBack: false
        }
      },
      {
        path: '/setting/local',
        name: 'SettingLocal',
        component: () => import('../views/setting/components/local.vue'),
        meta: {
          title: '自建服务器模式',
          showBack: false
        }
      },
      {
        path: '/setting/user-detail',
        name: 'SettingUserDetail',
        component: () => import('../views/setting/components/user-detail.vue'),
        meta: {
          title: '用户详情',
          showBack: false
        }
      },
      {
        path: '/setting/code-login',
        name: 'SettingCodeLogin',
        component: () => import('../views/setting/components/code-login.vue'),
        meta: {
          title: '重置密码',
          showBack: false
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 需要登录才能访问的路由
const authRoutes = ['/setting/user-detail', '/home', '/order', '/transition']

router.beforeEach(async (to, from, next) => {
  console.log(to)
  try {
    // 如果是访问根路径，直接显示 loading 页面
    if (to.path === '/') {
      next()
      return
    }

    const token = getToken()
    const userInfo = getUserInfo()
    const settingConfig = await getSettingConfig()
    const runModelType = settingConfig.run_model_type

   

    if ((runModelType === 0 || !runModelType) && to.path !== '/setting/login' && to.path !== '/setting/local') {
      next('/setting/login')
      return
    }
    if (to.path === '/setting/login' && runModelType === 1) {
      next('/setting/local')
      return
    }

    // 如果需要登录但未登录
    if (runModelType !== 1 && authRoutes.includes(to.path) && !token) {
      next('/setting/login')
      return
    }

    if (runModelType !== 1 && to.path === '/setting/login' && userInfo && token) {
      next('/setting/user-detail')
      return
    }

    // 如果有 token 但没有用户信息，尝试获取用户信息
    if (runModelType !== 1 && token && !userInfo) {
      try {
        const userInfo = await fetchUserInfo()
        setUserInfo(userInfo)
        // 如果当前在登录页，自动跳转到用户明细页
        if (to.path === '/setting/login') {
          next('/user/detail')
          return
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 如果获取用户信息失败，清除 token 并跳转到登录页
        clearAuth()
        next('/setting/login')
        return
      }
    }
    next()
  } catch (error) {
    console.error('路由导航失败:', error)
    // next('/setting/login')
  }
})

export default router
