# 使用轻量级Nginx镜像作为基础
FROM nginx:alpine

# 删除默认的Nginx配置
RUN rm -rf /etc/nginx/conf.d/default.conf

# 将打包后的文件复制到Nginx的默认静态文件目录
COPY dist-v4 /usr/share/nginx/html

# 复制自定义Nginx配置（如果有）
COPY nginx.conf /etc/nginx/conf.d/

# 暴露5173端口
EXPOSE 5173

# 启动Nginx（前台运行）
CMD ["nginx", "-g", "daemon off;"]