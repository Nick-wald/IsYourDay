import {service} from '../utils/request'

export const getFileList = (file_range: string) => {
  return service.get(`/file/list/${file_range}`)
}

export const uploadFile = (data: any) => {
  return service.post('/file/upload', data, {
    headers: {
      'Content-Type': 'multipart/form-data' // 关键设置
    }
  })
}

export const downloadFileStream = (file_id:string) => {
  return service.get(`/file/${file_id}/stream`)
}

export const fileDetail = (file_id: string) => {
  return service.get(`/file/${file_id}`)
}
