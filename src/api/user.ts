// import axios from 'axios'
import {service} from '../utils/request'

// 获取虚拟用户列表
export const getUserList = (skip: number, limit:number) => {
  return service.get('/isyourday/users', {params: {skip, limit }})
}

// 获取全部虚拟用户列表
export const getAllUser = () => {
  return service.get('/isyourday/users')
}

// 查找虚拟用户详情
export const findUserById = (user_id:string ) => {
  return service.get(`/isyourday/user/${user_id}`)
}

// 注册用户
export const addUser = (data: any) => {
  return service.post('/auth/register', data, {headers: {"Content-Type": "application/x-www-form-urlencoded"}})
}

// 添加虚拟用户
export const addVirtualUser = (data: any) => {
  return service.post('/isyourday/user', data)
}

// 删除虚拟用户
export const delVirtualUser = (data:any) => {
  return service.delete('/isyourday/users/batch', {data: data})
}

// 更新虚拟用户
export const editUserMsg = (user_id:string, data: any) => {
  return service.patch(`/isyourday/user/${user_id}`, data)
}

// 用户登录
export const userLogin = (data:any) => {
  return service.post('/auth/login', data, {
  headers: {
    'Content-Type': 'multipart/form-data' // 关键设置
  }
})
}

// 搜索虚拟用户
export const searchUser = (query: string) => {
  return service.get('/isyourday/users/search', {params: {query}})
}

export const getManagerList = () => {
  return service.get('/auth/users')
}

// 查找管理员用户详情
export const searchManager = (user_search_role:string, user_search_value:string) => {
  return service.get(`/auth/profile/${user_search_role}/${user_search_value}`)
}