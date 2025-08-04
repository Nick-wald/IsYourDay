<script setup>
import { ref } from 'vue';
import { userLogin, addUser } from '@/api/user.ts';
import { useRouter } from 'vue-router';
import { 登录鉴权Service } from '@/client';
import { ElMessage } from 'element-plus';
// 表单模式：登录或注册
const isLoginMode = ref(true);
const router = useRouter()
// 表单数据
const formData = ref({
  username: '',
  password: '',
  email: ''
});

// 错误信息

// 提交状态
const isSubmitting = ref(false);
const statusMessage = ref('');

// 切换登录/注册模式
const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value;
  // 清空表单和错误信息
  formData.value = {
    username: '',
    password: '',
    email: ''
  }
  // Object.keys(formData).forEach(key => formData[key] = '');
  // Object.keys(errors).forEach(key => errors[key] = '');
  statusMessage.value = '';
};

// 表单验证规则



// 提交表单
const handleSubmit = async () => {
  if (isLoginMode.value) {
    const form = new FormData()
    form.append('grant_type', 'password')
    form.append('scope', "auth:read_basic auth:read_all auth:write auth:delete file:read file:upload file:write file:delete isyourday:read isyourday:write isyourday:delete")
    form.append('username', formData.value.username)
    form.append('password', formData.value.password)
    // const res = await userLogin({grant_type: 'password',scope: "auth:read_basic auth:read_all auth:write auth:delete file:read file:upload file:write file:delete isyourday:read isyourday:write isyourday:delete", username: formData.value.username, password: formData.value.password})
    const res = await userLogin(form)
    
    // const res = await userLogin({grant_type: 'password', scope: "auth:read_basic auth:read_all auth:write auth:delete file:read file:upload file:write file:delete isyourday:read isyourday:write isyourday:delete",username: formData.value.username, password: formData.value.password})
    localStorage.setItem('token_type', res.data.token_type)
    localStorage.setItem('access_token',res.data.access_token)
    if(res.status >= 200 &&res.status < 300) {
      router.push('/')
    }
  }
  else {
    // const res = await 登录鉴权Service.registerUserAuthRegisterPost({email: formData.value.email, username: formData.value.username, password: formData.value.password})
    const res = await addUser({email: formData.value.email, username: formData.value.username, password: formData.value.password})
    if(res.status === 200) {
      isLoginMode.value = true
    }
    else {
      ElMessage.error(res.data.detail)
    }
  }
  
};
</script>

<template>
  <div class="auth-container">
    <div class="auth-form">
      <h2>{{ isLoginMode ? '登录' : '注册' }}</h2>
      
      <div>
        <div class="div-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="formData.username" 
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="formData.password" 
          />
        </div>
        
        <div class="form-group" v-if="!isLoginMode">
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="formData.email" 
          />
        </div>
        
        <button @click="handleSubmit" :disabled="isSubmitting">
          {{ isLoginMode ? '登录' : '注册' }}
        </button>
      </div>
      
      <p class="toggle-mode" @click="toggleMode">
        {{ isLoginMode ? '没有账号？点击注册' : '已有账号？点击登录' }}
      </p>
      
      <div class="status-message" v-if="statusMessage">
        {{ statusMessage }}
      </div>
    </div>
  </div>
</template>



<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.auth-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input {
  width: calc(100% - 1.75rem);
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #646cff;
}

.error-message {
  color: #ff4d4f;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #646cff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
}

button:hover {
  background-color: #535bf2;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.toggle-mode {
  text-align: center;
  margin-top: 1rem;
  color: #646cff;
  cursor: pointer;
}

.toggle-mode:hover {
  text-decoration: underline;
}

.status-message {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 4px;
  text-align: center;
}

.status-message.success {
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.status-message.error {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}
</style>