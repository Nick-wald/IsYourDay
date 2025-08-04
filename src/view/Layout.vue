<script setup lang="ts">
// import { authInit, redirectToAuthPage } from '../utils/authUtils'
import { RouterLink, RouterView, useRouter } from 'vue-router'
// import { ref } from 'vue'
// authInit(true)
const router = useRouter()

const open = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('token_type')
  router.push('/login')
}

</script>

<template>
  <div class="sidebar">
    <div class="logo">
       <div class="img"></div>
    </div>
    <ul class="nav-menu">
      <li><router-link to="/user" class="nav-link">用户管理</router-link></li>
      <li><router-link to="/event" class="nav-link">事件管理</router-link></li>
      <li><router-link to="/workflow" class="nav-link">工作流管理</router-link></li>
      <li><router-link to="/uploadFile" class="nav-link">Excel上传</router-link></li>
      <li><router-link to="/sendemail" class="nav-link">发送邮件</router-link></li>
      <li><router-link to="/mailhistory" class="nav-link">邮件历史</router-link></li>
      <div href="#" @click="open" class="btn danger-btn">登出</div>
    </ul>
  </div>

  <!-- 主内容区 -->
  <div class="main-content">
    <!-- 顶部导航 -->
    <router-view></router-view>
  </div>
</template>

<style scoped>
body{
  padding: 0;
  margin: 0;
}
/* 基础布局样式 */
.sidebar {
  width: 240px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background-color: #ffffff; /* 白色背景 */
  color: #333; /* 深色文字 */
  transition: all 0.3s ease;
  z-index: 1000;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  border-right: 1px solid #e5e5e5; /* 添加右边框 */
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #e5e5e5; /* 浅色分割线 */
}

.logo .img {
  max-width: 100%;
  height: 50px;
  background: url('../../public/logo.png') no-repeat;
  background-size: 100%;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 20px 0;
}

.nav-menu li {
  margin: 5px 0;
}

.nav-link {
  display: block;
  padding: 12px 20px;
  color: #555; /* 中等灰色文字 */
  text-decoration: none;
  transition: all 0.3s;
  font-size: 14px;
  border-left: 3px solid transparent;
}

.nav-link:hover {
  color: #1890ff; /* 悬停蓝色 */
  background-color: #f5f5f5; /* 浅灰背景 */
  border-left-color: #1890ff;
}

.nav-link.router-link-exact-active {
  color: #1890ff;
  background-color: #f0f7ff; /* 浅蓝色背景 */
  border-left-color: #1890ff;
  font-weight: 500;
}

.main-content {
  margin-left: 240px;
  min-height: 100vh;
  transition: all 0.3s ease;
  background-color: #f8f8f8;
  padding: 10px;
  box-sizing: border-box;
  overflow-y: auto;
}

/* 按钮样式 */
.btn {
  display: inline-block;
  padding: 10px 15px;
  margin: 10px 20px;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.danger-btn {
  background-color: #ff4d4f;
  color: white;
  border: none;
  width: calc(100% - 40px);
  transform: translateX(-16px);
}

.danger-btn:hover {
  background-color: #ff7875;
}

/* 平板适配 (768px-1024px) */
@media (max-width: 1024px) {
  .sidebar {
    width: 200px; /* 稍微缩小宽度 */
  }
  
  

  .main-content {
    margin-left: 200px;
  }
  
  .nav-link {
    padding: 10px 15px;
    font-size: 13px;
  }
}

/* 小型平板 (600px-768px) */
@media (max-width: 768px) {
  .sidebar {
    width: 64px;
    overflow: hidden;
  }
  
  .logo {
    padding: 15px 15px;
  }
  
  .logo .img {
    max-width: 100%;
    height: 38px;
    background: url('../../public/logo.svg') no-repeat;
    background-size: 100%;
  }
  
  .nav-link {
    padding: 10px 0;
    text-align: center;
    font-size: 0; /* 隐藏文字 */
    position: relative;
  }
  
  /* 使用图标代替文字 */
  .nav-link::before {
    font-family: "Font Awesome 5 Free";
    font-weight: 900;
    font-size: 18px;
    display: block;
    color: #666;
  }
  
  .nav-link[href*="user"]::before {
    content: "\f007"; /* 用户图标 */
  }
  
  .nav-link[href*="event"]::before {
    content: "\f073"; /* 日历图标 */
  }
  
  .nav-link[href*="workflow"]::before {
    content: "\f0e8"; /* 流程图标 */
  }
  
  .nav-link[href*="userdetail"]::before {
    content: "\f2bb"; /* 用户详情图标 */
  }
  
  .nav-link[href*="sendemail"]::before {
    content: "\f0e0"; /* 邮件图标 */
  }

  .nav-link[href*="uploadFile"]::before {
    content: "\f15b"; /* 文档图标 */
  }

  .nav-link[href*="mailhistory"]::before {
    content: "\f1da"; /* 历史记录图标（时钟） */
  }
  
  .nav-link:hover::before,
  .nav-link.router-link-exact-active::before {
    color: #1890ff;
  }
  
  .danger-btn {
    font-size: 0;
    padding: 12px 0;
    margin: 10px 0;
    width: 100%;
    transform: translateX(0);
  }
  
  .danger-btn::before {
    content: "\f2f5"; /* 登出图标 */
    font-family: "Font Awesome 5 Free";
    font-weight: 900;
    font-size: 18px;
    display: block;
  }
  
  .main-content {
    margin-left: 64px;
  }
}

/* 手机适配 (<600px) */
@media (max-width: 600px) {
  .sidebar {
    width: 56px; /* 更紧凑的宽度 */
    overflow: hidden;
    transform: translateX(0); /* 保持可见 */
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }
  
  .logo {
    padding: 12px 10px;
    padding-bottom: 6px;
  }
  
  .logo .img {
    width: 100%;
    height: 40px;
  }
  
  .nav-link {
    padding: 14px 0;
    text-align: center;
    font-size: 0; /* 隐藏文字 */
    position: relative;
    border-left: none; /* 移除左边框 */
    border-right: 3px solid transparent; /* 改为右边框 */
  }
  
  /* 使用图标代替文字 */
  .nav-link::before {
    font-family: "Font Awesome 5 Free";
    font-weight: 900;
    font-size: 18px;
    display: block;
    color: #666;
  }
  
  .nav-link:hover {
    border-left: none;
    border-right-color: #1890ff;
  }
  
  .nav-link.router-link-exact-active {
    border-left: none;
    border-right-color: #1890ff;
  }
  
  .danger-btn {
    font-size: 0;
    padding: 14px 0;
    margin: 10px 0;
    width: 100%;
  }
  
  .danger-btn::before {
    content: "\f2f5"; /* 登出图标 */
    font-family: "Font Awesome 5 Free";
    font-weight: 900;
    font-size: 18px;
    display: block;
  }
  
  .main-content {
    margin-left: 56px;
  }
  
  /* 调整汉堡菜单为关闭按钮 */
  .hamburger-menu {
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 1000;
    width: 24px;
    height: 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    background: rgba(255, 255, 255, 0.9);
    padding: 8px;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .hamburger-menu span {
    display: block;
    height: 2px;
    width: 16px;
    background-color: #333;
    transition: all 0.3s;
    margin: 2px 0;
  }
  
  /* 移除遮罩层相关样式，因为不再需要 */
}
</style>