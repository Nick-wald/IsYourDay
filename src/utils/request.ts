import axios from "axios";
import { ElMessage } from "element-plus";

export const ApiBaseURL = import.meta.env.VITE_API_URL

export const service = axios.create({
    baseURL: ApiBaseURL,
    timeout: 5000,
})

service.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 这里可以获取完整的错误信息
    // ElMessage.error('error')
    console.log(error);
    
    return Promise.reject(error) // 将错误信息传递下去
  }
)

service.interceptors.request.use(config => {
    const access = localStorage.getItem('access_token')
    const type = localStorage.getItem('token_type')
    if (access != null) {
        // 请求头验证字段
        config.headers.Authorization = type + ' ' + access
        // config.headers["Content-Type"] = "application/x-www-form-urlencoded"
        
    }
    if(!config.headers["Content-Type"]) {
      config.headers["Content-Type"] = "application/json"
    }
    return config
})

// export const checkLogin = async () => {
//   try {
//     const res = await service.get('/auth/me');
    
//     // 更安全的 token 存储方式
//     const { token_type, access_token } = res.data;
//     localStorage.setItem('token_type', token_type);
//     localStorage.setItem('access_token', access_token);
    
//     return { success: true, data: res.data };
//   } catch (error: any) {
//     // 区分不同类型的错误
//     if (error.response) {
//       switch (error.response.status) {
//         case 401:
//           console.warn('Token expired or invalid');
//           // 可以尝试刷新 token 而不是直接跳转
//           break;
//         case 500:
//           console.error('Server error');
//           break;
//         default:
//           console.error('Request failed', error.response.status);
//       }
//     } else {
//       console.error('Network error', error.message);
//     }
    
//     // 清除无效的 token
//     localStorage.removeItem('token_type');
//     localStorage.removeItem('access_token');
    
//     // 可以添加重定向前的确认或延迟
//     setTimeout(() => {
//       window.location.href = `${window.location.origin}/login?redirect=${encodeURIComponent(window.location.pathname)}`;
//     }, 1000);
    
//     return { success: false, error };
//   }
// };