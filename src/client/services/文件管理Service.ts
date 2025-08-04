import type { Body_replace_file_content_file__file_id__replace_put } from '../models/Body_replace_file_content_file__file_id__replace_put';
import type { Body_update_file_info_file__file_id__patch } from '../models/Body_update_file_info_file__file_id__patch';
import type { Body_upload_file_chunk_file_upload_chunk_post } from '../models/Body_upload_file_chunk_file_upload_chunk_post';
import type { Body_upload_files_file_upload_post } from '../models/Body_upload_files_file_upload_post';
import type { FileDB } from '../models/FileDB';
import type { FileRangeRole } from '../models/FileRangeRole';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export type TDataGetFilesFileListFileRangeGet = {
                fileRange: FileRangeRole
/**
 * 返回的记录数
 */
limit?: number
/**
 * 跳过的记录数
 */
skip?: number
            }
export type TDataSearchFilesFileSearchGet = {
                /**
 * 是否全局搜索（包括非公开文件），开启此项需要管理员权限
 */
globalSearch?: boolean
limit?: number
/**
 * 仅搜索公开文件
 */
publicOnly?: boolean
/**
 * 搜索关键词
 */
q: string
skip?: number
            }
export type TDataGetUploadStatusFileUploadStatusFileIdGet = {
                fileId: string
            }
export type TDataGetFileFileFileIdGet = {
                fileId: string
            }
export type TDataUpdateFileInfoFileFileIdPatch = {
                fileId: string
formData?: Body_update_file_info_file__file_id__patch
            }
export type TDataDownloadFileFileFileIdDownloadGet = {
                fileId: string
            }
export type TDataGetDownloadInfoFileFileIdDownloadHead = {
                fileId: string
            }
export type TDataStreamFileFileFileIdStreamGet = {
                fileId: string
            }
export type TDataUploadFilesFileUploadPost = {
                formData: Body_upload_files_file_upload_post
            }
export type TDataUploadFileChunkFileUploadChunkPost = {
                formData: Body_upload_file_chunk_file_upload_chunk_post
            }
export type TDataReplaceFileContentFileFileIdReplacePut = {
                fileId: string
formData: Body_replace_file_content_file__file_id__replace_put
            }
export type TDataDeleteFilesBatchFileBatchDelete = {
                /**
 * 强制删除（即使物理文件不存在）
 */
force?: boolean
requestBody: Array<string>
            }
export type TDataCleanupOrphanedFilesFileCleanupOrphanedPost = {
                /**
 * 仅模拟运行，不实际删除
 */
dryRun?: boolean
/**
 * 是否清理所有用户的孤立文件，此项需要管理员权限
 */
globalCleanup?: boolean
            }
export type TDataCleanupTempFilesFileCleanupTempPost = {
                /**
 * 仅模拟运行，不实际删除
 */
dryRun?: boolean
/**
 * 是否清理所有用户的临时文件，此项需要管理员权限
 */
globalCleanup?: boolean
/**
 * 清理超过指定小时数的临时文件
 */
maxAgeHours?: number
            }
export type TDataGetStorageUsageFileStorageUsageGet = {
                /**
 * 是否获取全局存储使用情况（需要管理员权限）
 */
globalUsage?: boolean
            }

export class 文件管理Service {

	/**
	 * 获取文件列表
	 * 获取文件列表
	 * @returns FileDB Successful Response
	 * @throws ApiError
	 */
	public static getFilesFileListFileRangeGet(data: TDataGetFilesFileListFileRangeGet): CancelablePromise<Array<FileDB>> {
		const {
fileRange,
limit = 10,
skip = 0,
} = data;
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
	public static searchFilesFileSearchGet(data: TDataSearchFilesFileSearchGet): CancelablePromise<Array<FileDB>> {
		const {
globalSearch = false,
limit = 10,
publicOnly = false,
q,
skip = 0,
} = data;
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
	public static getFileStatsFileStatsGet(): CancelablePromise<unknown> {
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
	public static getUploadStatusFileUploadStatusFileIdGet(data: TDataGetUploadStatusFileUploadStatusFileIdGet): CancelablePromise<unknown> {
		const {
fileId,
} = data;
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
	public static getFileFileFileIdGet(data: TDataGetFileFileFileIdGet): CancelablePromise<FileDB> {
		const {
fileId,
} = data;
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
	public static updateFileInfoFileFileIdPatch(data: TDataUpdateFileInfoFileFileIdPatch): CancelablePromise<FileDB> {
		const {
fileId,
formData,
} = data;
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
	public static downloadFileFileFileIdDownloadGet(data: TDataDownloadFileFileFileIdDownloadGet): CancelablePromise<unknown> {
		const {
fileId,
} = data;
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
	public static getDownloadInfoFileFileIdDownloadHead(data: TDataGetDownloadInfoFileFileIdDownloadHead): CancelablePromise<unknown> {
		const {
fileId,
} = data;
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
	public static streamFileFileFileIdStreamGet(data: TDataStreamFileFileFileIdStreamGet): CancelablePromise<unknown> {
		const {
fileId,
} = data;
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
	public static uploadFilesFileUploadPost(data: TDataUploadFilesFileUploadPost): CancelablePromise<Record<string, unknown>> {
		const {
formData,
} = data;
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
	public static uploadFileChunkFileUploadChunkPost(data: TDataUploadFileChunkFileUploadChunkPost): CancelablePromise<unknown> {
		const {
formData,
} = data;
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
	public static replaceFileContentFileFileIdReplacePut(data: TDataReplaceFileContentFileFileIdReplacePut): CancelablePromise<FileDB> {
		const {
fileId,
formData,
} = data;
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
	public static deleteFilesBatchFileBatchDelete(data: TDataDeleteFilesBatchFileBatchDelete): CancelablePromise<unknown> {
		const {
force = false,
requestBody,
} = data;
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
	public static cleanupOrphanedFilesFileCleanupOrphanedPost(data: TDataCleanupOrphanedFilesFileCleanupOrphanedPost = {}): CancelablePromise<unknown> {
		const {
dryRun = true,
globalCleanup = false,
} = data;
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
	public static cleanupTempFilesFileCleanupTempPost(data: TDataCleanupTempFilesFileCleanupTempPost = {}): CancelablePromise<unknown> {
		const {
dryRun = true,
globalCleanup = false,
maxAgeHours = 24,
} = data;
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
	public static getStorageUsageFileStorageUsageGet(data: TDataGetStorageUsageFileStorageUsageGet = {}): CancelablePromise<unknown> {
		const {
globalUsage = false,
} = data;
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