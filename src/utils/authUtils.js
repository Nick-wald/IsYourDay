// authUtils.ts
import axios from "axios";
import { ElMessage } from "element-plus";
export const ApiBaseURL = 'https://api.nickwald.top'; // API基地址
export const checkURLParamsTicket = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('ticket');
};
export const checkLoginStatus = () => {
    return !((localStorage.getItem('access') == null || localStorage.getItem('refresh') == null));
};
export const clearLoginStatus = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
};
export const service = axios.create({
    baseURL: ApiBaseURL,
    timeout: 5000,
});
service.interceptors.response.use(response => {
    return response;
}, error => {
    // 这里可以获取完整的错误信息
    ElMessage.error(error.response.data.msg);
    return Promise.reject(error); // 将错误信息传递下去
});
service.interceptors.request.use(config => {
    const access = localStorage.getItem('access');
    if (access != null) {
        // 请求头验证字段
        config.headers.Authorization = 'Bearer ' + access;
    }
    return config;
});
// 初始化，放在入口文件App.vue的script里或main.ts最前面
// require_login：设置为true则检查是否登录
export const authInit = (require_login = false) => {
    getToken(require_login);
};
// token失效时刷新
export const refreshToken = () => {
    if (localStorage.getItem('refresh') != null) {
        service.post('account/refresh', {
            refresh: localStorage.getItem('refresh')
        }).then(res => {
            localStorage.setItem('access', res.data.access);
            window.location.reload();
        });
    }
};
// 重定向至登录页，同时登出
export const redirectToAuthPage = () => {
    if (checkURLParamsTicket()) {
        // url不干净需要先清理
        getToken();
        return;
    }
    clearLoginStatus();
    const url = new URL(window.location.href);
    window.location.href = `${ApiBaseURL}/account/auth/?from=${url.origin}&action=redirect`;
};
// 从服务器抓取token（如果有）
// require_login：设置为true则检查是否登录
export const getToken = (require_login = false) => {
    const ticket = checkURLParamsTicket();
    if (ticket != null) {
        service.get(`account/auth/?ticket=${ticket}`).then(res => {
            localStorage.setItem('access', res.data.access);
            localStorage.setItem('refresh', res.data.refresh);
            // 去除url中参数，避免重复请求
            const url = new URL(window.location.href);
            window.history.replaceState(null, '', url.origin);
            window.location.reload();
        });
    }
    else {
        if (require_login && !checkLoginStatus()) {
            redirectToAuthPage();
        }
    }
};
//# sourceMappingURL=authUtils.js.map