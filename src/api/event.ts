// import { service } from "../utils/request";
import {service} from '../utils/request'

export const getUserEvent = (user_id: string) => {
  return service.get(`/isyourday/user/${user_id}/events`)
}

export const addEventOrMsg = (user_id:string, data: any) => {
  return service.post(`/isyourday/user/${user_id}/events`, data)
}

export const updateEventOrMsg = (user_id:string, event_id:string, data: any) => {
  return service.patch(`/isyourday/user/${user_id}/event/${event_id}`, data)
}

export const delEventOrMsg = (user_id: string, data: any) => {
  // const obj = JSON.stringify(data)
  return service.delete(`/isyourday/user/${user_id}/events/batch`, {data: data})
}

export const sendemail = (email_type: string, formData: any) => {
  return service.post(`/auth/send-email/${email_type}`, formData, {
  headers: {
    'Content-Type': 'multipart/form-data' // 关键设置
  }
})
}

export const getEmailHistory = (search_type: string, data: any) => {
  return service.get(`/auth/send-email/history/${search_type}`, {params: data})
}

export const updateEmailHistory = (history_id: string, data: any) => {
  return service.patch(`/auth/send-email/history?history_id=${history_id}`, data)
}

export const sendPendingEmail = (history_id: string) => {
  return service.get(`/auth/send-email/pending/${history_id}`)
}