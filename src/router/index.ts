// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
// import { authInit } from '../utils/authUtils';
import { checkLogin } from '../utils/request';
const router = createRouter({
    history: createWebHistory('/'),
    routes: [
        {
            path: '/',
            component: () => import('../view/Layout.vue'), // 需要有一个父组件
            children: [
                {
                    path: 'user',
                    component: () => import('../view/User.vue')
                },
                {
                    path: 'event',
                    component: () => import('../view/Event.vue')
                },
                {
                    path: 'workflow',
                    component: () => import('../view/Workflow.vue')
                },
                {
                    path: 'sendemail',
                    component: () => import('../view/Email.vue')
                },
                {
                    path: 'uploadFile',
                    component: () => import('../view/excel.vue')
                },
                {
                    path: 'mailhistory',
                    component: () => import('../view/MailHistory.vue')
                },
                {
                    path: '',
                    redirect: 'user'
                }
            ]
        },
        {
      path: '/login',
      component: () => import('../view/login.vue')
    },
        {
            path: '/',
            redirect: '/layout'
        }
    ]
});

router.beforeEach((to, from, next) => {
  // to: 即将进入的目标路由
  // from: 当前导航正要离开的路由
  // next: 必须调用该方法来 resolve 这个钩子
  
  // 示例：检查用户是否登录
  if (to.path !== '/login') {
    // 如果路由需要认证且用户未登录，重定向到登录页
    const access = localStorage.getItem('access_token')
    const type = localStorage.getItem('token_type')
    // checkLogin()
    if (!access || !type) {
      next('/login')
    }
    next()
  } else {
    // 继续导航
    next()
  }
})

export default router;
//# sourceMappingURL=index.js.map