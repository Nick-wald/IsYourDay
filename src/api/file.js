import { service } from '../utils/request';
export const getFileList = (file_range) => {
    return service.get(`/file/list/${file_range}`);
};
export const uploadFile = (data) => {
    return service.post('/file/upload', data, {
        headers: {
            'Content-Type': 'multipart/form-data' // 关键设置
        }
    });
};
export const downloadFileStream = (file_id) => {
    return service.get(`/file/${file_id}/stream`);
};
export const fileDetail = (file_id) => {
    return service.get(`/file/${file_id}`);
};
//# sourceMappingURL=file.js.map