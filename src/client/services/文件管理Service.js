import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class 文件管理Service {
    /**
     * 获取文件列表
     * 获取文件列表
     * @returns FileDB Successful Response
     * @throws ApiError
     */
    static getFilesFileListFileRangeGet(data) {
        const { fileRange, limit = 10, skip = 0, } = data;
        return __request(OpenAPI, {
            method: 'GET',
            url: '/file/list/{file_range}',
            path: {
                file_range: fileRange
            },
            query: {
                skip, limit
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 搜索文件
     * 搜索文件
     * @returns FileDB Successful Response
     * @throws ApiError
     */
    static searchFilesFileSearchGet(data) {
        const { globalSearch = false, limit = 10, publicOnly = false, q, skip = 0, } = data;
        return __request(OpenAPI, {
            method: 'GET',
            url: '/file/search',
            query: {
                q, skip, limit, public_only: publicOnly, global_search: globalSearch
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取文件统计信息
     * 获取文件统计信息
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static getFileStatsFileStatsGet() {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/file/stats',
        });
    }
    /**
     * 查询分片上传状态
     * 查询分片上传状态
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static getUploadStatusFileUploadStatusFileIdGet(data) {
        const { fileId, } = data;
        return __request(OpenAPI, {
            method: 'GET',
            url: '/file/upload/status/{file_id}',
            path: {
                file_id: fileId
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取单个文件信息
     * 获取单个文件信息
     * @returns FileDB Successful Response
     * @throws ApiError
     */
    static getFileFileFileIdGet(data) {
        const { fileId, } = data;
        return __request(OpenAPI, {
            method: 'GET',
            url: '/file/{file_id}',
            path: {
                file_id: fileId
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 更新文件信息
     * 更新文件信息（文件名、公开状态等）
     * @returns FileDB Successful Response
     * @throws ApiError
     */
    static updateFileInfoFileFileIdPatch(data) {
        const { fileId, formData, } = data;
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/file/{file_id}',
            path: {
                file_id: fileId
            },
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 下载文件（支持断点续传）
     * 下载文件，支持断点续传和分片传输
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static downloadFileFileFileIdDownloadGet(data) {
        const { fileId, } = data;
        return __request(OpenAPI, {
            method: 'GET',
            url: '/file/{file_id}/download',
            path: {
                file_id: fileId
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取文件下载信息（用于断点续传）
     * 获取文件下载信息，支持HEAD请求用于断点续传
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static getDownloadInfoFileFileIdDownloadHead(data) {
        const { fileId, } = data;
        return __request(OpenAPI, {
            method: 'HEAD',
            url: '/file/{file_id}/download',
            path: {
                file_id: fileId
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 流式下载文件（在线预览）
     * 流式下载文件，适用于在线预览（如视频、音频、图片）
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static streamFileFileFileIdStreamGet(data) {
        const { fileId, } = data;
        return __request(OpenAPI, {
            method: 'GET',
            url: '/file/{file_id}/stream',
            path: {
                file_id: fileId
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 上传文件（支持大文件优化）
     * 上传文件，自动优化大文件处理，支持批量上传容错处理
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static uploadFilesFileUploadPost(data) {
        const { formData, } = data;
        return __request(OpenAPI, {
            method: 'POST',
            url: '/file/upload',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 分片上传文件
     * 分片上传文件，支持大文件断点上传
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static uploadFileChunkFileUploadChunkPost(data) {
        const { formData, } = data;
        return __request(OpenAPI, {
            method: 'POST',
            url: '/file/upload/chunk',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 替换文件内容
     * 替换文件内容，保持文件ID不变
     * @returns FileDB Successful Response
     * @throws ApiError
     */
    static replaceFileContentFileFileIdReplacePut(data) {
        const { fileId, formData, } = data;
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/file/{file_id}/replace',
            path: {
                file_id: fileId
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 批量删除文件
     * 批量删除文件
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static deleteFilesBatchFileBatchDelete(data) {
        const { force = false, requestBody, } = data;
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/file/batch',
            query: {
                force
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 清理孤立文件
     * 清理数据库中没有记录但物理存在的孤立文件
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static cleanupOrphanedFilesFileCleanupOrphanedPost(data = {}) {
        const { dryRun = true, globalCleanup = false, } = data;
        return __request(OpenAPI, {
            method: 'POST',
            url: '/file/cleanup/orphaned',
            query: {
                dry_run: dryRun, global_cleanup: globalCleanup
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 清理临时文件
     * 清理临时上传文件
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static cleanupTempFilesFileCleanupTempPost(data = {}) {
        const { dryRun = true, globalCleanup = false, maxAgeHours = 24, } = data;
        return __request(OpenAPI, {
            method: 'POST',
            url: '/file/cleanup/temp',
            query: {
                max_age_hours: maxAgeHours, dry_run: dryRun, global_cleanup: globalCleanup
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * 获取存储使用情况
     * 获取用户存储使用情况详细信息
     * @returns unknown Successful Response
     * @throws ApiError
     */
    static getStorageUsageFileStorageUsageGet(data = {}) {
        const { globalUsage = false, } = data;
        return __request(OpenAPI, {
            method: 'GET',
            url: '/file/storage/usage',
            query: {
                global_usage: globalUsage
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
//# sourceMappingURL=%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86Service.js.map